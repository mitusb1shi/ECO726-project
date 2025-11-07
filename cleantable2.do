**********************************************************************************************
*creating table 2
**********************************************************************************************
 
 log using "Table-2", replace

*TABLE 2 - EFFECTS ON ADULT LABOR MARKET OUTCOMES

cd "D:\measles_project"
use longrun_20002017acs_cleaned.dta, clear

set emptycells drop

set matsize 11000


foreach a in cpi_incwage cpi_incwage_no0 ln_cpi_income  poverty100 employed hrs_worked {

local controls i.bpl i.birthyr i.ageblackfemale i.bpl_black i.bpl_female i.bpl_black_female black female


*main specification 
reg `a' M12_exp_rate `controls' i.year ,  robust cluster(bplcohort)
outreg2 using Table-2.xml, append keep (M12_exp_rate) nocons dec(4) ctitle(`a'_main) addtext(Birth State FE, X, Birth Year FE, X, ACS Year FE, X, bpl-cohort cluster SE, X)

}


*means for outcome variables, pre and post

summ  cpi_incwage cpi_incwage_no0 ln_cpi_income poverty100 employed hrs_worked avg_10yr_measles_rate avg_12yr_measles_rate if exposure==0
summ  cpi_incwage cpi_incwage_no0 ln_cpi_income poverty100 employed hrs_worked avg_10yr_measles_rate avg_12yr_measles_rate if exposure>0
summ cpi_incwage cpi_incwage_no0 ln_cpi_income poverty100 employed hrs_worked avg_10yr_measles_rate if birthyr==1947 | birthyr==1948
summ cpi_incwage cpi_incwage_no0 ln_cpi_income poverty100 employed hrs_worked avg_10yr_measles_rate if birthyr==1963 | birthyr==1964


log close
