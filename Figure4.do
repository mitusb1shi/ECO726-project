
clear all
set more off

log using "Figure4", replace 


*FIGURE 4 - EVENT STUDIES - EFFECT OF MEALES VACCINE ON OTHER CHILDHOOD INFECTIOUS DISEASES

*Morbidity ES pictures other infectious diseases
foreach sub in Pertussis Mumps Rubella ChickenPox {
cd  "D:\measles_project"
use inc_rate_ES_winsor.dta, clear

 

*create interaction term for year and Measles pre vac level in state
local i = 1
while `i' <= 5 {

gen exp_Mpre_`i'=_Texp_`i'*avg_12yr_measles_rate

local i = `i' + 1 
}

local i = 7
while `i' <= 18 {

gen exp_Mpre_`i'=_Texp_`i'*avg_12yr_measles_rate

local i = `i' + 1 
}



reg `sub' exp_M* _Is* population _T* avg_12yr_measles_rate,  cluster(statefip) robust



regsave, ci pval

*drop the uneeded coefficients and add in the 0s for the omitted year
drop in 18/87

set obs 18
replace var = "exp_Mpre_6" in 18
replace coef = 0 in 18
replace stderr = 0 in 18
replace N = 1108 in 18
replace ci_lower = 0 in 18
replace ci_upper = 0 in 18


gen exp=0
replace exp=-6 if var=="exp_Mpre_1"
replace exp=-5 if var=="exp_Mpre_2"
replace exp=-4 if var=="exp_Mpre_3"
replace exp=-3 if var=="exp_Mpre_4"
replace exp=-2 if var=="exp_Mpre_5"
replace exp=-1 if var=="exp_Mpre_6"
replace exp=-0 if var=="exp_Mpre_7"
replace exp=1 if var=="exp_Mpre_8"
replace exp=2 if var=="exp_Mpre_9"
replace exp=3 if var=="exp_Mpre_10"
replace exp=4 if var=="exp_Mpre_11"
replace exp=5 if var=="exp_Mpre_12"
replace exp=6 if var=="exp_Mpre_13"
replace exp=7 if var=="exp_Mpre_14"
replace exp=8 if var=="exp_Mpre_15"
replace exp=9 if var=="exp_Mpre_16"
replace exp=10 if var=="exp_Mpre_17"
replace exp=11 if var=="exp_Mpre_18"


sort exp


*create event study graph
scatter coef ci* exp if exp>-6 & exp<11, 	c(l l l) cmissing(y n n) ///
						msym(i i i) lcolor(gray gray gray) lpatter(solid dash dash) lwidth(thick medthick medthick) ///
						yline(0, lcolor(black)) xline(-1, lcolor(black)) ///
						subtitle("`sub' rate by year (per 100,000)", size(small) j(left) pos(11)) ylabel( , nogrid angle(horizontal) labsize(small)) ///
						xtitle("Years relative to measles vaccine availability", size(small)) xlabel(-5(5)10, labsize(small)) ///
						legend(off) ///
						graphregion(color(white)) 
						


graph save Graph `sub'_Mpre_time_ES.gph, replace	

}


graph combine Pertussis_Mpre_time_ES.gph ChickenPox_Mpre_time_ES.gph Mumps_Mpre_time_ES.gph Rubella_Mpre_time_ES.gph 
graph save Graph Figure4.gph, replace


log close
