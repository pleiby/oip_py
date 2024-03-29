# %% [markdown]
# # OIP.py Oil Import Premium, Python Implementation

# %% [markdown]
#   Revision Documentation
#   --------------------------
#
# -*- coding: utf-8 -*-
#   """
#   Revised 2021_09_14
#
#   @author: Paul N. Leiby
#
#   OIP.py 09/14/2021
#       Reviewed and updated rand_dists_added.py
#
#   OIP_DEV_V16temp 11/8/2013
#       Corrected sign of mean for "Elas:Other NonOPEC Demand"
#   OIP_Dev_V15 10/10/2013
#   OIP_Dev_V14 05/23/2011
#       Updated SPR size in oilmkt_parameter_cases
#       Made share of US GDP spent on oil (sigma_oUS) potenially vary across cases
#           (Base vs. Opt are sigma_oUS_0 vs. sigma_oUS_k). But currently set sigma_oUS_0 = sigma_oUS_k
#       Note: model not fully tested for Opt case, or dual cases.
#       Elaborate premium component breakdown:
#           - adding E_MCdis_vul_deGDP_k, SR Disr marginal effect: demand on GDP sensitivity [times RhoD]
#           - return all in list pi_components
#   OIP_Dev_V13 05/22/2011
#       Tested version that replicates spreadsheet version (Oil_Import_Premium_2005_risk_v21main_2011Dev_v13.xls)
#       for individual randomly generated cases to within 5 decimal places,
#       as well and mean total premium after full simulation of 10000 iterations.
#   """
#
#

# %%
import numpy as np
import rand_dists_added as rda


# %% [markdown]
# ## Data Section

# %%
# ======================================================================
alt_parameter_cases = {  # parameter cases are organized in a dictionary of lists
    "KEY_PARAMETERS_ASSUMPTIONS": ["Low", "Mid", "High", "Mean", "RandomFix"],
    "GDP disr loss elasticity": [0.01, 0.032, 0.054, 0.03200, 0.032],
    "Ratio of Long-run GDP elas to SR GDP disr Elas": [0.25, 0.25, 0.25, 0.25000, 0.25],
    "Disruption reduction w/ imports": [0.00, 0.10, 0.30, 0.13333, 0.167004852],
    "OPEC LR Supply elasticity": [4.000, 1.000, 0.250, 1.76250, 3.10097298],
    "Shr Disr price incr anticipated": [1.00, 0.25, 0.00, 0.41667, 0.197115189],
    "Marg var tot (oil&nonoil) demand w/ ref imports": [0.00, 0.00, 0.00, 0.00, 0.00],
    "Marg var tot (oil&nonoil) demand w/ opt imports": [0.00, 0.00, 0.00, 0.00, 0.00],
    "Marg var of demand with imports": [0.00, 0.00, 0.00, 0.00, 0.00],
    # "Disruption Probabilities":                       #N/A    #N/A    #N/A    #N/A     #N/A
    # "Disruption Offsets":                             #N/A    #N/A    #N/A    #N/A     #N/A
    "Disruption Prob Case Selector": [5, 5, 5, 5.00000, 5],
    "Disruption Length (yrs)": [1, 1, 2, 1.25, 1],
    "SPR Policy (Disr fract offset)": [0.9999, 0.50, 0.50, 0.624975, 0.9999],
    "SPR Policy (SPR fraction used)": [1.00, 1.00, 1.00, 1.00000, 1.00],
    "Effective Fraction of SPR Draw": [1.00, 1.00, 1.00, 1.00000, 1.00],
    "LR elas of US oil demand": [-0.30, -0.266, -0.20, -0.25800, -0.266],
    "LR elas of US oil supply": [0.462, 0.462, 0.462, 0.462000, 0.462],
    "adj rate domestic oil demand": [0.20, 0.15, 0.10, 0.150000, 0.1],
    "adj rate domestic oil supply": [0.15, 0.15, 0.15, 0.15000, 0.15],
    "Elas:Other NonOPEC Supply": [0.400, 0.300, 0.200, 0.300000, 0.284717782],
    "Elas:Other NonOPEC Demand": [-0.400, -0.300, -0.200, -0.30000, -0.284717782],
    "Oil Market (AEO) Case": [1, 2, 3, 2, 2],
}


# %%
oilmkt_parameter_cases = {
    # "Base_Mkt_Alts":                                    ["AEO2010 LWOP Price Path", "AEO2010 Base Price Path", "AEO2010 HWOP Price Path", "AEO2010 Base Price Path",  "AEO2010 Base Price Path"],
    "import oil price": [39.97700, 79.16172, 124.83358, 79.16172, 79.16172],
    "domestic oil demand": [21.68697, 20.66809, 20.24781, 20.66809, 20.66809],
    "domestic oil production": [9.73701, 9.96885, 10.27467, 9.96885, 9.96885],
    "domestic demand for oil substitutes (gas)": [
        6.31011,
        6.31011,
        6.31011,
        6.31011,
        6.31011,
    ],
    "undisrupted GDP": [14275.72, 14127.06, 13990.43, 14127.06, 14127.07],
    "SPR Size (MMB)": [727.0000, 727.0000, 727.0000, 727.0000, 688.0000],
    "NonUS Net Import Demand": [31.94905, 26.68243, 23.28659, 26.68243, 26.68243],
    "OPEC Supply": [43.89535, 37.38150, 33.25998, 37.38150, 37.38150],
    "Total World Supply": [96.38438, 90.91604, 82.64448, 90.91604, 90.91604],
    "OECD_Europe as Fraction of NonUS Consumption": [
        0.204719,
        0.204447,
        0.203969,
        0.204447,
        0.204447,
    ],
}


# %%
# dictionary of parameter name string (key),
#   param prob distribution-type string,
#   and vector of distribution parameters.
parameter_probabilities = {
    # Probability Cases":                                                     ["Low",  "Mid",  "High"]
    "GDP disr loss elasticity": ["risk_discrete", [0.25, 0.5, 0.25]],
    "Ratio of Long-run GDP elas to SR GDP disr Elas": [
        "risk_discrete",
        [0.25, 0.5, 0.25],
    ],
    "Disruption reduction w/ imports": [
        "risk_triangular",
        [],
    ],  # =RiskTriang(O10,P10,Q10)
    "OPEC LR Supply elasticity": ["risk_cumul", [0.0, 6.0, [0.1, 0.5, 0.9]]],
    "Shr Disr price incr anticipated": [
        "risk_rtriangular",
        [],
    ],  # =RiskTriang(Q12,P12,O12)
    "Marg var tot (oil&nonoil) demand w/ ref imports": [
        "risk_rtriangular",
        [],
    ],  # =RiskTriang(Q12,P12,O12)
    "Marg var tot (oil&nonoil) demand w/ opt imports": [
        "risk_rtriangular",
        [],
    ],  # =RiskTriang(Q12,P12,O12)
    "Marg var of demand with imports": [
        "risk_rtriangular",
        [],
    ],  # =RiskTriang(Q12,P12,O12)
    # "Disruption Probabilities":
    # "Disruption Offsets":
    "Disruption Prob Case Selector": [
        "risk_rtriangular",
        [],
    ],  # =RiskTriang(Q12,P12,O12)
    "Disruption Length (yrs)": [
        "risk_discrete",
        [0.25, 0.5, 0.25],
    ],  # =RiskDiscrete(O19:Q19,U19:W19)
    "SPR Policy (Disr fract offset)": [
        "risk_discrete",
        [0.25, 0.5, 0.25],
    ],  # =RiskDiscrete(O19:Q19,U19:W19)
    "SPR Policy (SPR fraction used)": [
        "risk_rtriangular",
        [],
    ],  # =RiskTriang(Q12,P12,O12)
    "Effective Fraction of SPR Draw": [
        "risk_rtriangular",
        [],
    ],  # =RiskTriang(Q12,P12,O12)
    "LR elas of US oil demand": [
        "risk_discrete",
        [0.25, 0.5, 0.25],
    ],  # =RiskDiscrete(O19:Q19,U19:W19)
    "LR elas of US oil supply": [
        "risk_discrete",
        [0.25, 0.5, 0.25],
    ],  # =RiskDiscrete(O19:Q19,U19:W19)
    "adj rate domestic oil demand": [
        "risk_discrete",
        [0.25, 0.5, 0.25],
    ],  # =RiskDiscrete(O19:Q19,U19:W19)
    "adj rate domestic oil supply": [
        "risk_rtriangular",
        [],
    ],  # =RiskTriang(Q12,P12,O12)
    "Elas:Other NonOPEC Supply": ["risk_rtriangular", []],  # =RiskTriang(Q12,P12,O12)
    # Elas:Other NonOPEC Demand":                        [= above            , []],
    "Oil Market (AEO) Case": [
        "risk_discrete",
        [0.00, 1.0, 0.00],
    ],  # =RiskDiscrete(O19:Q19,U19:W19)
}


# %%
# Decadal Disruption Probabilities and sizes
disr_size_prob_cases = {
    "DisrSize": [1.0, 3.0, 6.0],  # MMBD  - exog - Disr Size
    "Case0": [0.00, 0.00, 0.00],  # unitless  - exog - Decade Probs
    "Case1": [0.50, 0.10, 0.05],  # unitless  - exog - Decade Probs
    "Case2": [0.75, 0.30, 0.05],  # unitless  - exog - Decade Probs
    "Case3": [0.95, 0.50, 0.20],  # unitless  - exog - Decade Probs
    "Case4DOE90": [0.08, 0.06, 0.01],  # unitless  - exog - Decade/Annual? Probs
    "Case5EMF2005": [
        0.252633052143075,
        0.364353207172899,
        0.127087131573051,
    ],  # unitless  - exog - Decade Probs
}

disrSizes = np.array(disr_size_prob_cases["DisrSize"])
disrProbs = np.array(disr_size_prob_cases["Case5EMF2005"])


# %% [markdown]
#   """ Random distributions needed:
#       RiskDiscrete(XList,DiscProbList)
#       RiskTriang(XLowBnd,XMode,XUpBnd)
#       =RiskCumul(XlowBnd,XUpBnd,{XList0.25,1,4},{CumProbList 0.1,0.5,0.9})
#
#   =RiskDiscrete(O6:Q6,U6:W6)
#   GDP disr loss elasticity
#   GDP-oil Price elast, Long-run/Short-run
#   Disruption Length (yrs)
#   SPR Policy (Disr fract offset)
#   LR elas of US oil demand
#   LR elas of US oil supply
#   adj rate domestic oil demand
#
#   adj rate domestic oil supply
#   =RiskTriang(Q26,P26,O26) (but one value)
#
#   =RiskTriang(O10,P10,Q10)
#   Disruption reduction w/ imports
#   Shr Disr price incr anticipated
#   Marg var tot (oil&nonoil) demand w/ imports0
#   Marg var tot (oil&nonoil) demand w/ imports1
#   Marg var of demand with imports
#   SPR Policy (SPR fraction used)
#   Effective Fraction of SPR Draw
#   Elas:Other NonOPEC Supply
#   Elas:Other NonOPEC Demand
#   = Elas:Other NonOPEC Supply (before any adjustment due to constrained demand)
#   Disruption Prob Case Selector
#   =RiskTriang(Q18,P18,O18), but only one value
#
#   =RiskCumul(0,6,{0.25,1,4},{0.1,0.5,0.9})
#   OPEC LR Supply elasticity
#
#   = deterministic (no distribution, not varying in risk analysis)
#   Disruption Probabilities
#   Disruption Offsets
#
#   = exog
#   Oil Market (AEO) Case
#   """
#

# %%
def init_OIP(replicable=False):
    """Initialize variables, parameters, and random functions for OIP.
    Parameter replicable=False if random seed is to be "randomized" based on system clock.
    """
    if replicable:
        np.random.seed(1)  # initialize seed based a particular starting point
    else:
        np.random.seed()  # initialize seed based on system clock


# %%
OIP_default_switches = [
    2010,  # Switch_AEOVersion
    2015,  # Switch_Year
    1.0,  # Switch_DomDem_ElasMult
    0.0,
]  # Switch_ConstrOECDEurDemand


# %%
def test_mult_cases(num_samples=1):
    """test utility to complete one OIP calculation or set of variant calculations

    numsamples -- =-1 for one case with current default switches and parms,
    or >1 for spec set of variant cases (e.g. varying one parameter).
    Also uses current year market data in `oilmkt_parameter_cases`

    returns single vector of total premium results, or list of vectors \n
    requires globals `alt_parameter_cases`, `disrSizes`, `disrProbs`, `OIP_default_switches`
    """

    global alt_parameter_cases, disrSizes, disrProbs, OIP_default_switches
    sample_results = []
    switches = OIP_default_switches
    if num_samples == -1:  # default case with debug == True
        sample_results = eval_one_case(
            alt_parameter_cases, disrSizes, disrProbs, switches, debug=True
        )
    else:  # test desired set of cases
        for n in range(num_samples):
            switches[2] = 1.0 + np.random.normal(
                0.0, 0.25
            )  # test: alt values of Switch_DomDem_ElasMult
            sample_results.append(
                eval_one_case(
                    alt_parameter_cases, disrSizes, disrProbs, switches
                )  # [0] if want `pi_tot` only
            )
            if n % 100 == 0:
                print(n)
    return sample_results


# %% [markdown]
# ### `eval_one_case()`: Evaluation of a single case (Monte Carlo iteration, year, input set)

# %%
def eval_one_case(alt_parameter_cases, disrSizes, disrProbs, OIP_switches, debug=False):
    """complete OIP calculation one year and set of param values

    alt_parameter_cases -- dict of param values for Low, Mid, High, Random & Fixed cases;
    disrSizes --;
    disrProbs --;
    OIP_switches -- list of switches also governing cases;
    debug=False -- print report on premium components if True\n
    return `pi_components` a vector (list) of premium components and diagnostics for this one case\n

    requires globals `oilmkt_parameter_cases` (selected case based on `alt_parameter_cases`)
    """

    Switch_AEOVersion = OIP_switches[0]
    Switch_Year = OIP_switches[1]
    Switch_DomDem_ElasMult = OIP_switches[2]
    Switch_ConstrOECDEurDemand = OIP_switches[
        3
    ]  # Switch indicating whether the OECD Europe share of Non-US demand is to be treated as fixed

    # ======================================================================
    # Get parameter values associated with this selected Case
    currcase = 4  # 4 is RandomFixed from test case; 3 is Random

    # VarName                         Notes   # KEY PARAMETERS/ASSUMPTIONS                                                  # (Units       )
    newversion = False
    if newversion:
        sigma_usto = alt_parameter_cases["Tight Oil Fraction of US Supply"][
            currcase
        ]  # (Unitless)
    u_gdp = alt_parameter_cases["GDP disr loss elasticity"][currcase]  # (Unitless)
    ru_gdp = alt_parameter_cases["Ratio of Long-run GDP elas to SR GDP disr Elas"][
        currcase
    ]  # (Percent) GDP-oil Price elast, Long-run/Short-run   <-Unused-> - Exog -
    dEDelQ_dq_i = alt_parameter_cases["Disruption reduction w/ imports"][
        currcase
    ]  # (Percent)
    dlnQsodlnP = alt_parameter_cases["OPEC LR Supply elasticity"][
        currcase
    ]  # (Unitless)
    Rho_E = alt_parameter_cases["Shr Disr price incr anticipated"][
        currcase
    ]  # (Percent)
    dQ_t_dq_i0 = alt_parameter_cases["Marg var tot (oil&nonoil) demand w/ ref imports"][
        currcase
    ]  # (Percent)
    dQ_t_dq_i1 = alt_parameter_cases["Marg var tot (oil&nonoil) demand w/ opt imports"][
        currcase
    ]  # (Percent)
    Rho_D = alt_parameter_cases["Marg var of demand with imports"][
        currcase
    ]  # (Percent) =dq_d_dq_i
    # -x-                             = alt_parameter_cases["Disruption Probabilities"][currcase]                            # (-x-         )
    # -x-                             = alt_parameter_cases["Disruption Offsets"][currcase]                                  # (-x-         )
    case_probs = alt_parameter_cases["Disruption Prob Case Selector"][
        currcase
    ]  # (Integer     )
    L_disr = alt_parameter_cases["Disruption Length (yrs)"][currcase]  # (Years)
    F_o = alt_parameter_cases["SPR Policy (Disr fract offset)"][currcase]  # (Percent)
    F_r = alt_parameter_cases["SPR Policy (SPR fraction used)"][currcase]  # (Percent)
    F_e = alt_parameter_cases["Effective Fraction of SPR Draw"][currcase]  # (Percent)
    n_dlr = alt_parameter_cases["LR elas of US oil demand"][currcase]  # (Unitless)
    n_slr = alt_parameter_cases["LR elas of US oil supply"][currcase]  # (Unitless)
    A_d = alt_parameter_cases["adj rate domestic oil demand"][
        currcase
    ]  # (Percent/yr  )
    A_s = alt_parameter_cases["adj rate domestic oil supply"][
        currcase
    ]  # (Percent/yr  )
    e_SNOr = alt_parameter_cases["Elas:Other NonOPEC Supply"][currcase]  # (Unitless)
    e_DNOr = alt_parameter_cases["Elas:Other NonOPEC Demand"][currcase]  # (Unitless)
    case_oilmkt = alt_parameter_cases["Oil Market (AEO) Case"][currcase]  # (Unitless)
    case_oilmktndx = int(round(case_oilmkt - 1))  # ToDo: chk strange xform
    n_dlr = (
        n_dlr * Switch_DomDem_ElasMult
    )  # (adjusted) LR elas of US oil demand (Unitless)

    GDP_0 = oilmkt_parameter_cases["undisrupted GDP"][case_oilmktndx]  # ($bill/yr)
    # GDP_1 = GDP_0
    Q_SPR = oilmkt_parameter_cases["SPR Size (MMB)"][case_oilmktndx]  # (Mill BBL)

    # OTHER EXOG INPUT: Base Mkt Supply, Demand and Price Conditions
    # These params may differ between Base and Opt premium case
    P_i0 = oilmkt_parameter_cases["import oil price"][case_oilmktndx]  # ($/BBL)
    # ($/BBL) P_i0 Exog , P_i1 = P_i0 + dP_i_dq_i1 *(q_i1-q_i0)
    q_d0 = oilmkt_parameter_cases["domestic oil demand"][case_oilmktndx]  # (MMBD)
    q_s0 = oilmkt_parameter_cases["domestic oil production"][case_oilmktndx]  # (MMBD)
    q_n0 = oilmkt_parameter_cases["domestic demand for oil substitutes (gas)"][
        case_oilmktndx
    ]  # (MMBD)
    # q_n1 = q_n0
    q_INonUS_0 = oilmkt_parameter_cases["NonUS Net Import Demand"][
        case_oilmktndx
    ]  # (MMBD)
    S_OPEC = oilmkt_parameter_cases["OPEC Supply"][case_oilmktndx]  # (MMBD)
    S_tot = oilmkt_parameter_cases["Total World Supply"][
        case_oilmktndx
    ]  # <-Unused-> - Exog -   # (MMBD)
    sigma_EurNon = oilmkt_parameter_cases[
        "OECD_Europe as Fraction of NonUS Consumption"
    ][
        case_oilmktndx
    ]  # (Unitless shr) (Opt Same as Base)

    # ======================================================================
    #  Derived Parameters - Part 1
    """
    P_d0                            P_d0 = P_i0, P_d1 chosen by solver   # domestic oil price ($/BBL)
    q_i0                            q_i0 = q_d0 - q_s0   # oil import level (MMBD)
    T_0                             T_k = P_dk - P_ik, but t_0 = 0 and Unused, T_1 = P_d1 - p_i1 determined by solver choice of P_d1   # Implicit tariff ($/BBL)
    S_NO_k                          <-Unused-> S_NO_0 = S_tot - S_OPEC - q_s0; S_NO_1 = S_NO_0*(P_i1/P_i0)**e_SNO   # Other NonOPEC Supply (MMBD)
    S_iToUS_k                       <-Unused-> S_iToUS_0 = S_OPEC - q_INonUS_0 (Need to subtract OPEC demand); S_iToUS_1 = S_iToUS_1*(P_i1/P_i0)**e_SNetToUS_0    # Net Import Supply to US (MMBD)
    q_DNonUS_k                      q_DNonUS_0 = q_INonUS_0 + S_NO_0; q_DNonUS_1 = q_DNonUS_0*(P_i1/P_i0)**e_DNO   # Other NonOPEC Demand (MMBD)
    """

    F_DNO_fixed = (
        sigma_EurNon * Switch_ConstrOECDEurDemand
    )  # Fraction of NonUS-NonOPEC demand which is fixed (Unitless)
    e_SNO = e_SNOr  # Elas:Other NonOPEC Supply (Unitless) Alt same as Base
    e_DNO = e_DNOr * (
        1.0 - F_DNO_fixed
    )  # Elas:Other NonOPEC Demand, adjusted (Unitless) Alt same as Base
    # Elas:Other NonOPEC Demand,  Alt same as Base (Unitless)

    # Variables - Reference (non-Opt import level) values
    P_d0 = P_i0  # domestic oil price (P_d1 chosen by solver) ($/BBL)
    q_i0 = q_d0 - q_s0  # oil import level (q_ik same formula)(MMBD)
    T_0 = P_d0 - P_i0  # Implicit tariff ($/BBL)
    # T_k = P_dk - P_ik, but T_0 = 0 and Unused, T_1 = P_d1 - P_i1 determined by solver choice of P_d1   # Implicit tariff ($/BBL)
    S_NO_0 = S_tot - S_OPEC - q_s0  # Other NonOPEC Supply <-Unused-> (MMBD)
    #   S_NO_1 = S_NO_0*(P_i1/P_i1)**e_SNO
    S_iToUS_0 = (
        S_OPEC - q_INonUS_0
    )  # Net Import Supply to US  (Need to subtract OPEC demand) <-Unused->(MMBD)
    #   S_iToUS_1 = S_iToUS_0*(P_i1/P_i0)**e_SNetToUS_0  # Net Import Supply to US (MMBD)
    q_DNonUS_0 = q_INonUS_0 + S_NO_0  # Other NonOPEC Demand (MMBD)
    #   q_DNonUS_1 = q_DNonUS_0*(P_i1/P_i0)**e_DNO     # Other NonOPEC Demand (MMBD)

    # ======================================================================
    # Create temporary values for _some_ "alt case" variables (Opt), just matching Ref, or "0" case.
    # In future any variable subscripted by k should  be a vector indexed by 0 and 1 (Ref and Opt case)
    # (UPDATE FOR DUAL CASE)
    q_dk = q_d0
    q_sk = q_s0
    q_ik = q_i0
    q_nk = q_n0
    P_dk = P_d0
    P_ik = P_i0
    GDP_k = GDP_0

    # ======================================================================
    #  Derived Parameters - part 2
    """
    sigma_Or                        Reference Level Exog   # Share: OPEC Supply as Share of World (Unitless)
    e_INonUS                        - Exog -   # Elas:NonUS Net Import Demand (Unitless)
    e_SOPEC                         - Exog - Taken from Above = dlnQsodlnP  # Elas:OPEC Supply (Unitless)
    e_SNO                           <-Unused-> - Exog -   # Elas:Other NonOPEC Supply (Unitless)
    e_DNO                           - Exog -   # Elas:Other NonOPEC Demand (Unitless)
    F_DNO_fixed                     # Fraction of NonUS-NonOPEC demand which is fixed (Unitless)
    Chkn_SRdUS                      <-Unused-> Chkn_SRdUS = n_dlr * A_d   # Elas: SR Elas US Oil dmnd (chk) (Unitless)
    Chkn_SRsUS                      <-Unused-> Chkn_SRsUS = n_slr * A_s   # Elas: SR Elas US Oil supl (chk) (Unitless)
    sigma_eUS                       <-Unused-> sigma_eUS = P_ik * (q_dk + q_nk) * 0.365/GDP_k   # share of GDP spent on oil and related products (Percent)
    sigma_oUS_k                     sigma_oUS_k = P_ik * (q_dk) * 0.365/GDP_k   # share of GDP spent on oil [Used for demand effects on GDP sens. ] (Percent)
    e_iu_k                          <-Unused-> e_iu_k == (Chkn_SRdUS*q_dk-Chkn_SRsUS*q_sk)/(q_dk-q_sk)   # Elas: SR Elas of US import dem (computed, info) (Unitless)

    sigma_Or        = 0.0           # Share: OPEC Supply as Share of World (Unitless) = S_OPEC/S_tot
    e_INonUS        = 0.0           # Elas:NonUS Net Import Demand (Unitless) '- Exog - Base== (e_DNO*q_DNonUS_0-e_SNO*S_NO_0)/(q_DNonUS_0-S_NO_0), Alt = Base
    e_SOPEC         = 0.0           # Elas:OPEC Supply (Unitless) - Exog - Taken from Above
    F_DNO_fixed     = 0.0           # Fraction of NonUS-NonOPEC demand which is fixed (Unitless)
    Chkn_SRdUS      = 0.0           # Elas: SR Elas US Oil dmnd (chk) (Unitless) <-Unused-> Chkn_SRdUS = n_dlr * A_d
    Chkn_SRsUS      = 0.0           # Elas: SR Elas US Oil supl (chk) (Unitless) <-Unused-> Chkn_SRsUS = n_slr * A_s
    sigma_eUS       = 0.0           # share of GDP spent on oil and related products (Percent) <-Unused-> sigma_eUS = P_ik * (q_dk + q_nk) * 0.365/GDP_k
    sigma_oUS_k     = 0.0           # share of GDP spent on oil (Percent) <-Unused-> sigma_oUS = P_ik * (q_dk) * 0.365/GDP_k
    e_iu_k          = 0/0           # Elas: SR Elas of US import dem (computed, info) (Unitless) <-Unused-> e_iu_k == (Chkn_SRdUS*q_dk-Chkn_SRsUS*q_sk)/(q_dk-q_sk)
    """
    # Todo: Some following are valid for k in {0,1}, others must be differentiated
    sigma_Or = S_OPEC / S_tot  # Share: OPEC Supply as Share of World (Unitless)
    e_INonUS = (e_DNO * q_DNonUS_0 - e_SNO * S_NO_0) / (
        q_DNonUS_0 - S_NO_0
    )  # Elas:NonUS Net Import Demand (Unitless)
    e_INonUS_1 = e_INonUS  # Alt same as Base (Unitless)
    e_SOPEC = dlnQsodlnP  # Elas:OPEC Supply (Unitless)
    e_SOPEC_1 = e_SOPEC  # Alt same as Base (Unitless)

    e_SNetToUS_0 = (S_OPEC * e_SOPEC - q_INonUS_0 * e_INonUS) / (
        S_OPEC - q_INonUS_0
    )  # Elas:Net Import Supply to US (Unitless)
    # e_SNetToUS_1 = (S_OPEC * e_SOPEC - q_INonUS_1 * e_INonUS) / (S_OPEC - q_INonUS_1)
    # e_SNetToUS_k = (S_OPEC * e_SOPEC - q_INonUS_k * e_INonUS) / (S_OPEC - q_INonUS_k)   # Elas:Net Import Supply to US (Unitless)
    Chkn_SRdUS = n_dlr * A_d  # Elas: SR Elas US Oil dmnd (chk) (Unitless)
    Chkn_SRsUS = n_slr * A_s  # Elas: SR Elas US Oil supl (chk) (Unitless)
    sigma_eUS = (
        P_i0 * (q_d0 + q_n0) * 0.365 / GDP_0
    )  # share of GDP spent on oil and related products (Percent)
    # sigma_eUS      = P_ik * (q_dk + q_nk) * 0.365/GDP_k   # share of GDP spent on oil and related products (Percent)
    sigma_oUS_0 = P_i0 * (q_d0) * 0.365 / GDP_0  # share of GDP spent on oil (Percent)
    # sigma_oUS_k    = P_ik * (q_dk) * 0.365/GDP_k   # share of GDP spent on oil (Percent)
    e_iu_0 = (Chkn_SRdUS * q_d0 - Chkn_SRsUS * q_s0) / (
        q_d0 - q_s0
    )  # Elas: SR Elas of US import dem (computed, info) (Unitless)
    # e_iu_k         = (Chkn_SRdUS*q_dk-Chkn_SRsUS*q_sk)/(q_dk-q_sk)   # Elas: SR Elas of US import dem (computed, info) (Unitless)

    # Create temporary values for _some_ "alt case" variables (Opt), just matching Ref, or "0" case.
    # (UPDATE FOR DUAL CASE)
    sigma_oUS_k = sigma_oUS_0

    """
    # FIXED PARAMETERS (OTHER)                                          (            )

    Base                               # Base                                                              (            )
    VarName                         Equation Notes   # Trial                                                             (Units)
    R_O                             Opt Same as Base: - exog - (specified here)   # oil inflation rate in real terms (%/yr)                           ((%/yr)      )
    dR_O_dQi                        Opt Same as Base: - exog - (specified here)   # derivative of oil inflation w.r.t. imports                        ((%/yr)/mmbd )
    Phi                             Opt Same as Base: - exog - (specified here)   # Phillip's curve derivative (%unempl/%infl reduction)              (%/%         )
    Beta                            Opt Same as Base: - exog - (specified here)   # Okun's law ratio (%lost output/%unemployment)                     (%GDP/%U     )
    n_pe                            Opt Same as Base: - exog - (specified here)   # elasticity of oil import price w.r.t. exchange rate (Unitless)
    n_X                             Opt Same as Base: - exog - (specified here)   # price elas of demand for exports (Unitless)
    n_M                             Opt Same as Base: - exog - (specified here)   # price elas of demand for non-oil imports (Unitless)
    n_isr                           Opt Same as Base: - exog - (specified here)   # SR imported oil supply elasticity (generates param "b") (Unitless)
    dP_i_dq_i                       Opt Same as Base: dP_i_dq_i = 1/(e_SNetToUS_0*q_i0/P_i0)   # derivative of normal market (LR?) inverse import supply (($/bbl)/MMBD)
    u_gdp                           Opt Same as Base: (reproduced from above Key Parameter block)   # (absolute) elasticity of GDP w.r.t. oil price shock (Unitless)
    dEDelQ_dq_i                     Opt Same as Base: (reproduced from above Key Parameter block)   # change in Disruption size per unit change in LR import demand     (unitless (MM)
    F_o                             Opt Same as Base: (reproduced from above Key Parameter block)   # fraction of disruption offset by SPR (if greater) (Unitless)
    Rho_E                           Opt Same as Base: (reproduced from above Key Parameter block)   # Share of disruption price increase anticipated (Unitless)
    n_dlr                           Opt Same as Base: (reproduced from above Key Parameter block)   # LR elas of US oil demand (Unitless)
    n_slr                           Opt Same as Base: (reproduced from above Key Parameter block)   # LR elas of US oil supply (Unitless)
    A_d                             Opt Same as Base: (reproduced from above Key Parameter block)   # adjustment rate for domestic oil demand (Unitless)
    A_s                             Opt Same as Base: (reproduced from above Key Parameter block)   # adjustment rate for domestic oil supply (Unitless)
    Q_SPR                           Opt Same as Base: (reproduced from above Key Parameter block)   # SPR Size (MMB) (MMB)
    F_r                             Opt Same as Base: (reproduced from above Key Parameter block)   # fraction of SPR used to offset (if greater)                       (unitless fra)
    F_e                             Opt Same as Base: (reproduced from above Key Parameter block)   # Effective Fraction of SPR Draw offsetting disruption (Unitless)
    """
    # ======================================================================
    # FIXED PARAMETERS (OTHER)

    # VarName                               Equation Notes   # Trial                                                             (Units)
    R_O = 0.034  # Opt Same as Base: - exog - (specified here)   # oil inflation rate in real terms (%/yr)                           ((%/yr))
    dR_O_dQi = 0.001  # Opt Same as Base: - exog - (specified here)   # derivative of oil inflation w.r.t. imports                        ((%/yr)/mmbd )
    Phi = 2.0  # Opt Same as Base: - exog - (specified here)   # Phillip's curve derivative (%unempl/%infl reduction)              (%/%)
    Beta = 2.0  # Opt Same as Base: - exog - (specified here)   # Okun's law ratio (%lost output/%unemployment)                     (%GDP/%U)
    n_pe = (
        -1.0
    )  # Opt Same as Base: - exog - (specified here)   # elasticity of oil import price w.r.t. exchange rate (Unitless)
    n_X = (
        -2.0
    )  # Opt Same as Base: - exog - (specified here)   # price elas of demand for exports (Unitless)
    n_M = (
        -1.5
    )  # Opt Same as Base: - exog - (specified here)   # price elas of demand for non-oil imports (Unitless)
    n_isr = 0.100  # Opt Same as Base: - exog - (specified here)   # SR imported oil supply elasticity (generates param "b") (Unitless)
    dP_i_dq_i = 1 / (  # Opt Same as Base:
        e_SNetToUS_0 * q_i0 / P_i0
    )  # derivative of normal market (LR?) inverse import supply (($/bbl)/MMBD)

    # ======================================================================
    """
    # INTERMEDIATE CALCULATIONS                                         (            )

    VarName                         Equation Notes   # Trial                                                             (Units       )
    b_isSR                          Opt Same as Base: b_isSR =dq_is/dP_i0 = n_isr *(q_i0/P_i0)   # price slope for SR import supply curve (MMBD/($/BBL))
    c_idSR                          Opt Same as Base: c_idSR  =-dq_id/dP_i = -(n_dlr * A_d* q_d0 - n_slr*A_s*q_s0)/q_i0*(q_i0/P_d0)   # (minus) price slope for SR import demand curve (MMBD/($/BBL))
    dq_d_dP_dk                      dq_d_dP_dk  = n_dlr * q_dk/P_dk   # derivative, LR domestic demand for oil (MMBD/($/BBL))
    dq_s_dP_d                       Opt Same as Base: dq_s0_dP_d0 = n_slr * q_s0/ P_d0   # derivative, LR domestic supply for oil (MMBD/($/BBL))
    n_dsr                           { Unused } Opt Same as Base: n_dsr = n_dlr * A_d   # SR elas of US oil demand (Unitless)
    n_ssr                           { Unused } Opt Same as Base: n_ssr = n_slr * A_s   # SR elas of US oil supply (Unitless)
    dQ_t_dq_ik                      dQ_t_dq_i0 = exog from above   # LR derivative total (oil&subst) demand w.r.t. import demand (Unitless)
    dP_ddq_ik                       dP_ddq_ik = 1/(dq_d_dP_dk - dq_s_dP_d) (formerly calculated from LR demand elas by dP_ddq_ik =(1/$n_dlr)*$P_d0/$q_d0)   # derivative, LR domestic inverse import demand curve (($/bbl)/MMBD)
    W_0                             w_k = 1 - Sum(j, w_kj)   # scale factor for tariff loss during Disruption (Unitless)
    dq_d_dq_i                       Opt Same as Base: dq_d_dq_i = Rho_D = exog (formerly calculated by equilib outcome =$n_dlr*$q_d0/($N_ILR0*$q_i0) (assuming what about tariff?)
    n_ilr0                          <-Unused-> Opt Same as Base: n_ilrk = ( n_dlr * q_dk - n_slr* q_sk) / q_ik (actually, treated as same for k=1 and k=0)   # LR elas of US imports demand (Unitless)
    n_nlr                           n_nlr = exog (from above = n_dlr LR elas of oil demand???)   # LR elas of US oil subst demand (Unitless)
    D_1                             { UNUSED } D_1 = + (b_isSR+ c_idSR+ q_dk*u_gdp/P_dk)/(b_isSR+c_idSR)   # work array to calc s.r. derivatives in t4 and t5                  ({???}       )
    D_2                             { UNUSED } D_2 = +(dQ_t_dq_ik * (u_gdp/P_dk) - q_dk*(u_gdp/P_dk**2) * dP_ddq_ik)/(b_isSR+c_idSR)   # work array to calc s.r. derivatives in t4 and t5                  ({???}       )
    D_3k                            D_3k = +dQ_t_dq_ik * (u_gdp / P_dk)-q_dk * (u_gdp/ P_dk**2)* dP_ddq_ik   # work array to calc s.r. derivatives in t4 and t5 (= d(e/Delp)/dq_ ({???}       )
    D_4                             { UNUSED } D_4 = dq_d_dq_i * (u_gdp/P_dk) - q_dk*(u_gdp/P_dk**2) * dP_ddq_ik   # work array to calc s.r. derivatives in t4 and t5 (= d(e/Delp)/dq_ ({???}       )
    dE_tdq_i0                       { UNUSED } dE_tdq_ik  = dQ_t_dq_ik*P_dk + dP_i_dq_i * (q_dk+q_nk)    # derivative, oil & related expenditures w.r.t. imports             (($/yr_or_day)
                                       #                                                                   (            )
    """

    # NEXT ----------------------
    # INTERMEDIATE CALCULATIONS

    b_isSR = n_isr * (
        q_i0 / P_i0
    )  # price slope for SR import supply curve = dq_is/dP_i0.  Opt Same as Base) (MMBD/($/BBL))
    c_idSR = (
        -(n_dlr * A_d * q_d0 - n_slr * A_s * q_s0) / q_i0 * (q_i0 / P_d0)
    )  # (minus) price slope for SR import demand curve= -dq_id/dP_i, Opt Same as Base) (MMBD/($/BBL))
    dq_d_dP_dk = (
        n_dlr * q_dk / P_dk
    )  # derivative, LR domestic demand for oil (MMBD/($/BBL))
    dq_s_dP_d = (
        n_slr * q_s0 / P_d0
    )  # derivative, LR domestic supply for oil (Opt Same as Base) (MMBD/($/BBL))
    n_dsr = (
        n_dlr * A_d
    )  # SR elas of US oil demand ({ Unused } Opt Same as Base) (Unitless)
    n_ssr = (
        n_slr * A_s
    )  # SR elas of US oil supply ({ Unused } Opt Same as Base) (Unitless)
    n_eqk = 0  # price elas of exchange rate w.r.t. oil import price (Unitless)
    dQ_t_dq_ik = dQ_t_dq_i0  # (UPDATE FOR DUAL CASE) LR derivative total (oil&subst) demand w.r.t. import demand (= exog from above) (Unitless)
    dP_ddq_ik = 1 / (
        dq_d_dP_dk - dq_s_dP_d
    )  # (formerly calculated from LR demand elas by dP_ddq_ik =(1/$n_dlr)*$P_d0/$q_d0)   # derivative, LR domestic inverse import demand curve (($/bbl)/MMBD)
    dq_d_dq_i = Rho_D  # (Opt Same as Base) = exog (formerly calculated by equilib outcome =$n_dlr*$q_d0/($N_ILR0*$q_i0) (assuming what about tariff?)
    n_ilr0 = (
        n_dlr * q_d0 - n_slr * q_s0
    ) / q_i0  # (actually, treated as same for k=1 and k=0)   # LR elas of US imports demand (Unitless)
    n_ilrk = (
        n_dlr * q_dk - n_slr * q_sk
    ) / q_ik  # (actually, treated as same for k=1 and k=0)   # LR elas of US imports demand (Unitless)
    n_nlr = n_dlr  # exog (Opt Same as Base) (from above = n_dlr LR elas of oil demand (???)   # LR elas of US oil substitute demand (Unitless)
    D_1 = +(b_isSR + c_idSR + q_dk * u_gdp / P_dk) / (
        b_isSR + c_idSR
    )  # work array to calc s.r. derivatives in t4 and t5                  ({???}       )
    D_2 = +(dQ_t_dq_ik * (u_gdp / P_dk) - q_dk * (u_gdp / P_dk**2) * dP_ddq_ik) / (
        b_isSR + c_idSR
    )  # work array to calc s.r. derivatives in t4 and t5                  ({???}       )
    D_3k = (
        +dQ_t_dq_ik * (u_gdp / P_dk) - q_dk * (u_gdp / P_dk**2) * dP_ddq_ik
    )  # work array to calc s.r. derivatives in t4 and t5 (= d(e/Delp)/dq_ ({???}       )
    D_4 = (
        dq_d_dq_i * (u_gdp / P_dk) - q_dk * (u_gdp / P_dk**2) * dP_ddq_ik
    )  # work array to calc s.r. derivatives in t4 and t5 (= d(e/Delp)/dq_ ({???}       )
    dE_tdq_i0 = dE_tdq_ik = dQ_t_dq_ik * P_dk + dP_i_dq_i * (
        q_dk + q_nk
    )  # derivative, oil & related expenditures w.r.t. imports { UNUSED } (($/yr_or_day)

    # ======================================================================
    """
    # Disruption Work Calculations                                      (            )

    Equation Notes   #                                                                   (Units)
    DeltaQ_g_j                      DeltaQ_g_j = exog (case dependent)   # DeltaQ_G, Gross shortfall to U.S. (MMBD)
    S_SPR_j                         S_SPR_j = MINA(F_o*DeltaQ_g_j/F_e,+F_r*Q_SPR/(L_disr*365))   # SPRDraw Rate (MMBD) (MMBD)
    S_SPRoff_j                      S_SPRoff_j = S_SPR_j * F_e   # SPROffset, SPRDraw allocated to US (MMBD)
    Prob10_j                        Prob10_j = exog (case dependent)   # Decade_P  (Unitless)
    Prob_Yj                         Prob_yj = 1 - (1-Prob10_j)**(1/10)   # Yearly_P  (Unitless)
    DelP_Delq_k                     DelP_Delq_k = 1/(B + C + q_dk*u_gdp/P_dk)   # SR (Disruption) Price Slope (($/bbl)/MMBD)
    DeltaQ_kj                       DeltaQ_j = DeltaQ_g_j - S_SPR_j   # DeltaQ, net shortfall to U.S. (MMBD)
    DeltaP_kj                       DeltaP_kj = Delp/Delq_k * DeltaQ_kj   # DeltaP, Calc ($/BBL)
                                       # -superceded                                                       (            )
    GDPl_kj                         <-Unused-> GDPl_kj = GDP_k*(1-u_gdp*DeltaP_kj/P_dk)   # Linear GDP Calc ($bill/yr)
    GDPe_kj                         GDPe_kj = GDP_k*((DeltaP_kj+P_dk)/P_dk)**(-u_gdp)   # Elastic GDP Calc ($bill/yr)
                                       # -superceded                                                       (            )
    Q_t_kj                          Q_t_kj = q_ik-q_dk*u_gdp*DeltaP_kj/P_dk   # SR GNP-shifted import demand (MMBD)
    Q_r_kj                          {!Neg dmnd?}  Q_rkj = q_ik-q_dk*u_gdp*DeltaP_kj/P_dk-c_idSR*DeltaP_kj   # SR import demand (GNP and price effect) (MMBD)
    dDelPdqi_kj                     dDelPdqi_kj = dDeltaP_kj/dq_i = -DeltaQ_kj*(DeltaP_kj/DeltaQ_kj)**2*D_3k+dEDelQ_dq_i*(DeltaP_kj/DeltaQ_kj)   # Derivative, DeltaP w.r.t. undisr imports (($/bbl)/MMBD)
    dQ_tdq_i_kj                     dQ_tdq_i_kj = =1-dQ_t_dq_ik*u_gdp*DeltaP_kj/P_d1-q_d1*u_gdp*dDelPdqi_kj/P_d1+q_d1*u_gdp*DeltaP_kj*dP_ddQ_i1/P_d1**2   # Derivative, SR GNP_shifted demand w.r.t. undisr imports           (unitless (MM)
    dQ_udq_i_kj                     dQ_udq_i_kj = dQ_tdq_i_kj - c_idSR*dDelPdqi_kj   # Derivative, SR imp supply w.r.t. undisr imports                   (unitless (MM)
    dQ_sdq_i_kj                     {UNUSED, =dQ_udq_i_kj} dQ_sdq_i_kj = 1- dEDelQ_dq_i+ b_isSR * dDelPdqi_kj   # Derivative, SR imp demand w.r.t. undisr imports                   (unitless (MM)
                                       #                                                                   (            )
    MCdis_x1                        MCdis_vul_monops_kj = +(Q_t_kj - Q_r_kj)*($dP_ddq_ik-$dP_i_dq_i)   # MCdis_vul_monops_kj ($/BBL)
    MCdis_x2                        MCdis_vul_dGDP_kj = -u_gdp * GDPe_kj*DeltaP_kj* dP_ddq_ik/P_dk**2   # MCdis_vul_dGDP_kj ($/BBL)
    MCdis_x3                        MCdis_vul_dDWL_kj = =0.5* DeltaP_kj * (dQ_tdq_i_kj - dQ_udq_i_kj)   # MCdis_vul_dDWL_kj ($/BBL)
    MCdis_x4                        MCdis_vul_dFC_kj = DeltaP_kj * (dQ_udq_i_kj - Rho_E)   # MCdis_vul_dFC_kj ($/BBL)
    pMCdis_x1                       Prob_Yj * MCdis_vul_monops_kj   # Prob_weighted ... ($/BBL)
    pMCdis_x2                       Prob_Yj * MCdis_vul_dGDP_kj   # Prob_weighted ... ($/BBL)
    pMCdis_x3                       Prob_Yj * MCdis_vul_dDWL_kj   # Prob_weighted ... ($/BBL)
    pMCdis_x4                       Prob_Yj * MCdis_vul_dFC_kj   # Prob_weighted ... ($/BBL)
    pMCdis_x1_4                     = pMCdis_x1 + pMCdis_x2 + pMCdis_x3 pMCdis_x4   # Test Sum     ($/BBL)
    t_4_j                           MCdis_vul_kj = MCdis_vul_monops_kj + MCdis_vul_dGDP_kj + MCdis_vul_dDWL_kj + MCdis_vul_dFC_kj   # MCdis_vul_kj ($/BBL)
    Prob_Yj_x_t_4_j                 = Prob_Yj * MCdis_vul_kj   # Prob_weighted t_4_j ($/BBL)
                                       #                                                                   (            )
    MCdis_x5                        MCdis_size_dSSdDWL_kj = 0.5*(Q_t_kj  - Q_r_kj)* dDelPdqi_kj   # MCdis_size_dSSdDWL_kj ($/BBL)
    MCdis_x6                        MCdis_size_dFC_kj = Q_r_kj * dDelPdqi_kj   # MCdis_size_dFC_kj ($/BBL)
    MCdis_x7                        MCdis_size_dGNPdDelP_kj = ($u_gdp* GDPe_kj /$P_dk) * dDelPdqi_kj   # MCdis_size_dGNPdDelP_kj ($/BBL)
    pMCdis_x5                       = Prob_Yj * MCdis_size_dSSdDWL_kj   # Prob_weighted ... ($/BBL)
    pMCdis_x6                       = Prob_Yj * MCdis_size_dFC_kj   # Prob_weighted ... ($/BBL)
    pMCdis_x7                       = Prob_Yj * MCdis_size_dGNPdDelP_kj   # Prob_weighted ... ($/BBL)
    pMCdis_x5_7                     = pMCdis_x5 + pMCdis_x6 + pMCdis_x7   # Test Sum     ($/BBL)
    t_5_j                           MCdis_size_kj = MCdis_size_dSSdDWL_kj + MCdis_size_dFC_kj + MCdis_size_dGNPdDelP_kj = (0.5*(Q_t_kj + Q_r_kj) + u_gdp*GDPe_kj/P_dk)* dDelPdqi_kj   # MCdis_size_kj ($/BBL)
    Prob_j_x_t_5_j                  = Prob_Yj * MCdis_size_kj   # Prob_weighted t_5_j ($/BBL)
    w_kj                            w_kj = Prob_Yj  * (dQ_tdq_i_kj - dQ_udq_i_kj)   # Weighting factor                                                  (unitless (MM)
    PrDeltaP_kj                     PrDeltaP_kj = Prob_Yj * DeltaP_kj   # Prob_weighted price Increase ($/BBL)
    S_TSPR_kj                       S_TSPR_kj = S_SPR_j * 365 * L_disr   # SPR Draw Total (MMB) (MMB)
                                       #                                                                   (            )
                                    <-Unused->   #                                                                   (            )
                                       # Diagnostics                                                       (EV Optimal  )
    E[DeltaQ_kj)                    = DeltaQ_kj * Prob_Yj   # Prob_weighted DeltaQ                                              (0.1049538289)
    E[DeltaP_kj)                    = DeltaP_kj * Prob_Yj   # Prob_weighted DeltaP                                              (2.9009435691)
                                       #                                                                   (            )
    E[DeltaGDPl_kj)                 = (GDP_0-GDPl_kj) * Prob_Yj   # Prob_weighted DeltaGDP (linear, GDP_0 - GDPl                      (14.392088997)
    E[DeltaGDPe_kj)                 = (GDP_0-GDPe_kj) * Prob_Yj   # Prob_weighted DeltaGDP (elastic, GDP_0 - GDPe)                    (10.688840289)
                                       #                                                                   (            )
    DeltaP/DeltaQ                   = DeltaP_kj/DeltaQ_kj   # Inverse Import Supply (Price) Slope (($/bbl)/MMBD)
                                       #                                                                   (            )
                                       #                                                                   (            )
                                       #                                                                   (            )
                                       #                                                                   (            )
                                       # CHECKS:                                                           (            )
    Chk_pi_m_elas                   = P_ik/e_SNetToUS_k   # Check: Monopsony Premium pi_m via elasticity                      (            )
    Chk_pi_m_slope                  = q_ik*dP_i_dq_i   # Check: Monopsony Premium pi_m via price slope                     (            )
    Chk_pi_m                        = pi_mk   # Monopsony Premium Reported                                        (            )
    """

    # -------------------------------
    # Disruption Work Calculations
    DeltaQ_g_j = disrSizes  # DeltaQ_G, Gross shortfall to U.S. (MMBD)
    S_SPR_j = np.minimum(
        F_o * DeltaQ_g_j / F_e, +F_r * Q_SPR / (L_disr * 365)
    )  # SPRDraw Rate (MMBD)
    S_SPRoff_j = S_SPR_j * F_e  # SPROffset, SPRDraw allocated to US (MMBD)
    Prob10_j = disrProbs  # Decade_P (exog, case dependent) (Unitless)
    Prob_Yj = 1.0 - (1.0 - Prob10_j) ** (1.0 / 10.0)  # Yearly_P  (Unitless)
    DelP_Delq_k = 1 / (
        b_isSR + c_idSR + q_dk * u_gdp / P_dk
    )  # SR (Disruption) Price Slope (($/bbl)/MMBD)
    DeltaQ_kj = DeltaQ_g_j - S_SPR_j  # DeltaQ, net shortfall to U.S. (MMBD)
    DeltaP_kj = DelP_Delq_k * DeltaQ_kj  # DeltaP, Calc ($/BBL)

    GDPl_kj = GDP_k * (
        1 - u_gdp * DeltaP_kj / P_dk
    )  # Linear GDP Calc (<-Unused-> ) ($bill/yr)
    GDPe_kj = GDP_k * ((DeltaP_kj + P_dk) / P_dk) ** (
        -u_gdp
    )  # Elastic GDP Calc ($bill/yr)

    Q_t_kj = (
        q_ik - q_dk * u_gdp * DeltaP_kj / P_dk
    )  # SR GNP-shifted import demand (MMBD)
    Q_r_kj = (
        q_ik - q_dk * u_gdp * DeltaP_kj / P_dk - c_idSR * DeltaP_kj
    )  # SR import demand (GNP and price effect) {!Neg dmnd?} (MMBD)
    dDelPdqi_kj = -DeltaQ_kj * (DeltaP_kj / DeltaQ_kj) ** 2 * D_3k + dEDelQ_dq_i * (
        DeltaP_kj / DeltaQ_kj
    )  # Derivative, DeltaP w.r.t. undisr imports, = dDeltaP_kj/dq_i (($/BBL)/MMBD)
    # dQ_tdq_i_kj  = 1-dQ_t_dq_ik*u_gdp*DeltaP_kj/P_d1-q_d1*u_gdp*dDelPdqi_kj/P_d1+q_d1*u_gdp*DeltaP_kj*dP_ddQ_i1/P_d1**2   # Derivative, SR GNP_shifted demand w.r.t. undisr imports           (unitless (MM)
    dQ_tdq_i_kj = (
        1
        - dQ_t_dq_ik * u_gdp * DeltaP_kj / P_dk
        - q_dk * u_gdp * dDelPdqi_kj / P_dk
        + q_dk * u_gdp * DeltaP_kj * dP_ddq_ik / P_dk**2
    )
    dQ_udq_i_kj = (
        dQ_tdq_i_kj - c_idSR * dDelPdqi_kj
    )  # Derivative, SR imp supply w.r.t. undisr imports                                                   (unitless (MM)
    dQ_sdq_i_kj = (
        1 - dEDelQ_dq_i + b_isSR * dDelPdqi_kj
    )  # Derivative, SR imp demand w.r.t. undisr imports  {UNUSED = dQ_udq_i_kj}                           (unitless (MM)

    MCdis_x1 = MCdis_vul_monops_kj = +(Q_t_kj - Q_r_kj) * (
        dP_ddq_ik - dP_i_dq_i
    )  # MCdis_vul_monops_kj ($/BBL)
    MCdis_x2 = MCdis_vul_dGDP_kj = (
        -u_gdp * GDPe_kj * DeltaP_kj * dP_ddq_ik / P_dk**2
    )  # MCdis_vul_dGDP_kj ($/BBL)
    MCdis_x3 = MCdis_vul_dDWL_kj = (
        0.5 * DeltaP_kj * (dQ_tdq_i_kj - dQ_udq_i_kj)
    )  # MCdis_vul_dDWL_kj ($/BBL)
    MCdis_x4 = MCdis_vul_dFC_kj = DeltaP_kj * (
        dQ_udq_i_kj - Rho_E
    )  # MCdis_vul_dFC_kj ($/BBL)
    pMCdis_x1 = Prob_Yj * MCdis_vul_monops_kj  # Prob_weighted ... ($/BBL)
    pMCdis_x2 = Prob_Yj * MCdis_vul_dGDP_kj  # Prob_weighted ...($/BBL)
    pMCdis_x3 = Prob_Yj * MCdis_vul_dDWL_kj  # Prob_weighted ...($/BBL)
    pMCdis_x4 = Prob_Yj * MCdis_vul_dFC_kj  # Prob_weighted ...($/BBL)
    pMCdis_x1_4 = pMCdis_x1 + pMCdis_x2 + pMCdis_x3 + pMCdis_x4  # Test Sum ($/BBL)
    t_4_j = MCdis_vul_kj = (
        MCdis_vul_monops_kj + MCdis_vul_dGDP_kj + MCdis_vul_dDWL_kj + MCdis_vul_dFC_kj
    )  # MCdis_vul_kj ($/BBL)
    Prob_Yj_x_t_4_j = Prob_Yj * MCdis_vul_kj  # Prob_weighted t_4_j ($/BBL)

    MCdis_x5 = MCdis_size_dSSdDWL_kj = (
        0.5 * (Q_t_kj - Q_r_kj) * dDelPdqi_kj
    )  # MCdis_size_dSSdDWL_kj ($/BBL)
    MCdis_x6 = MCdis_size_dFC_kj = Q_r_kj * dDelPdqi_kj  # MCdis_size_dFC_kj($/BBL)
    MCdis_x7 = MCdis_size_dGNPdDelP_kj = (
        u_gdp * GDPe_kj / P_dk
    ) * dDelPdqi_kj  # MCdis_size_dGNPdDelP_kj ($/BBL)
    pMCdis_x5 = Prob_Yj * MCdis_size_dSSdDWL_kj  # Prob_weighted ...($/BBL)
    pMCdis_x6 = Prob_Yj * MCdis_size_dFC_kj  # Prob_weighted ...($/BBL)
    pMCdis_x7 = Prob_Yj * MCdis_size_dGNPdDelP_kj  # Prob_weighted ...($/BBL)
    pMCdis_x5_7 = pMCdis_x5 + pMCdis_x6 + pMCdis_x7  # Test Sum ($/BBL)
    t_5_j = MCdis_size_kj = (
        MCdis_size_dSSdDWL_kj + MCdis_size_dFC_kj + MCdis_size_dGNPdDelP_kj
    )  # = (0.5*(Q_t_kj + Q_r_kj) + u_gdp*GDPe_kj/P_dk)* dDelPdqi_kj   # MCdis_size_kj ($/BBL)
    Prob_j_x_t_5_j = Prob_Yj * MCdis_size_kj  # Prob_weighted t_5_j ($/BBL)
    w_kj = Prob_Yj * (
        dQ_tdq_i_kj - dQ_udq_i_kj
    )  # Weighting factor                                                  (unitless (MM)
    PrDeltaP_kj = Prob_Yj * DeltaP_kj  # XXX Prob_weighted price Increase ($/BBL)
    S_TSPR_kj = S_SPR_j * 365 * L_disr  # SPR Draw Total (MMB) (MMB)

    # Diagnostics (Expected Values)
    E_DeltaQ_kj = DeltaQ_kj * Prob_Yj  # Prob_weighted DeltaQ (MMBD)
    E_DeltaP_kj = DeltaP_kj * Prob_Yj  # Prob_weighted DeltaP ($/BBL)

    E_DeltaGDPl_kj = (
        GDP_0 - GDPl_kj
    ) * Prob_Yj  # Prob_weighted DeltaGDP (linear, GDP_0 - GDPl ($bill)
    E_DeltaGDPe_kj = (
        GDP_0 - GDPe_kj
    ) * Prob_Yj  # Prob_weighted DeltaGDP (elastic, GDP_0 - GDPe) ($bill)

    DeltaP_over_DeltaQ = (
        DeltaP_kj / DeltaQ_kj
    )  # Inverse Import Supply (Price) Slope (($/bbl)/MMBD)

    # CHECKS:                                                           (            )
    # Chk_pi_m_elas                   = P_ik/e_SNetToUS_k   # Check: Monopsony Premium pi_m via elasticity                      (            )
    # Chk_pi_m_slope                  = q_ik*dP_i_dq_i   # Check: Monopsony Premium pi_m via price slope                     (            )
    # Chk_pi_m                        = pi_mk   # Monopsony Premium Reported                                        (            )

    w_k = 1 - np.sum(
        w_kj, 0
    )  # scale factor for tariff loss during Disruption (Unitless)
    # ToDo: w_k is bit low, and should be differentiated by 0,1
    # ======================================================================
    """
    # SIDE ANALYSIS:                                                    (            )
    Pi_m_theor                      = P_ik/e_SNetToUS_k   # Theoretical Monoposony Premium ($/BBL)

    dq_dNO_over_dq_iUS_theor        = e_DNO/e_SNetToUS_k*(q_DNonUS_k/S_iToUS) (compare to dq_dNO/dq_iUS)   # Theoretical: NonUS Demand Takeback, imports                       (Unitless (pe)

    = q_DNonUS/S_iToUS              = q_DNonUS/S_iToUS   # NonUS Supply as multiple of US imports                            (Unitless (MM)
    dq_iNO_over_dq_dUS              Note: assumes a tariff, causing an increase in U.S. production   # Diagnostic: NonUS Demand Takeback                                 (Unitless (pe)
    dq_iNO_over_dq_iUS              = (q_INonUS_1-q_INonUS_0)/(q_d1-q_d0)   # Diagnostic: NonUS Import Takeback                                 (Unitless (pe)
    dq_netNO_over_dq_iUS            = dq_sOPEC_over_dq_iUS - dq_iNO_over_dq_iUS   # Total Non-US net response (iNO + sOPEC)                           (Unitless (pe)
    TB_NOd_USi_v2                   = e_DNO*q_DNonUS/(e_SOPEC*S_OPEC + e_SNO*S_NO - e_DNO*q_DNonUS)   # Theoretical Takeback: dq_dNO/dq_iUS - revised form                (Unitless (pe)
    F_DNO_fixed_copy                = F_DNO_fixed  # Assumption: Fraction of NonUS-NonOPEC demand which is fixed       (Unitless (pe)




        MCdis_vul_monops_k              MCdis_vul_monops_k = sum(j,Prob_Yj*MCdis_vul_monops_kj)/w_k   #     SR Disr monoposony effect: marg effect on Price ($/BBL)
        MCdis_vul_dGDP_k                MCdis_vul_dGDP_k = sum(j,Prob_Yj*MCdis_vul_dGDP_kj)/w_k   #     SR Disr marginal effect on GDP loss ($/BBL)
        MCdis_vul_dDWL_k                MCdis_vul_dDWL_k = sum(j,Prob_Yj*MCdis_vul_dDWL_kj)/w_k   #     SR Disr marginal effect on DWL ($/BBL)
        MCdis_vul_dFC_k                 MCdis_vul_dFC_k = sum(j,Prob_Yj*MCdis_vul_dFC_kj)/w_k   #     SR Disr marginal effect on Foreign Claims ($/BBL)
      MCdis_vul_k                     MCdis_vul_k =     MCdis_vul_monops_k +     MCdis_vul_dGDP_k +     MCdis_vul_dDWL_k +     MCdis_vul_dFC_k   #   SR Dist marg effect on vulnerability costs ($/BBL)
        MCdis_size_dSSdDWL_k            MCdis_size_dSSdDWL_k = Sum(j, Prob_Yj*MCdis_size_dSSdDWL_kj)/w_k   #     SR Disr marg effect of size on DWL ($/BBL)
        MCdis_size_dFC_k                MCdis_size_dFC_k = Sum(j, Prob_Yj*MCdis_size_dFC_kj)/w_k   #     SR Disr marg effect of size on Foreign Claims ($/BBL)
        MCdis_size_dGNPdDelP_k          MCdis_size_dGNPdDelP_k = Sum(j, Prob_Yj*MCdis_size_dGNPdDelP_kj)/w_k   #     SR Disr marg effect of size on GDP loss ($/BBL)
      MCdis_size_k                    MCdis_size_k = MCdis_size_dSSdDWL_k + MCdis_size_dFC_k +  MCdis_size_k_dGNPdDelP_k   #   SR Disr marg effect of size on vuln costs ($/BBL)
                                       #                                                                   (            )
                                       #                                                                   (            )
                                       #                                                                   (            )
                                       #                                                                   (            )
                                       #                                                                   (            )
                                       #                                                                   (            )
                                       #                                                                   (            )
                                       #                                                                   (            )
                                       #                                                                   (            )
    IFConvTest                      =IF(ConvTest<0.00001,"TRUE","FALSE")   # ConvTest Report: (Unitless)
                                       #                                                                   (            )
                                       #                                                                   (            )
    # ======================================================================
                                    Equation Notes   # RECAP OF RESULTS                                                  (Units       )
    VarName                            # Results                                                           (            )
    P_i0                            (reproduced from below)   # Opt Import price ($/BBL)
      MCmonopsony                   (reproduced from below)   #   Monopsony Premium ($/BBL)
      MCbop                         (reproduced from below)   #   BOP Premium ($/BBL)
      MCinf                         (reproduced from below)   #   Inf Premium ($/BBL)
      MClr_pot                      (reproduced from below)   #   LR Potential Output Premium ($/BBL)
    MCLR                            (reproduced from below)   # Dependency (Long-run) Premium ($/BBL)
      MCdis_SS                      (reproduced from below)   #   SR Disruption DWL Premium ($/BBL)
      MCdis_FC                      (reproduced from below)   #   SR Disruption Foreign-Claims Premium ($/BBL)
      MCdis_GDP                     (reproduced from below)   #   SR Disruption GDP Dislocation Premium ($/BBL)
    MCdis                           (reproduced from below)   # Security (SR Disruption) Premium ($/BBL)
    MCtot                           (reproduced from below)   # Total Premium ($/BBL)
        MCdis_vul_monops_k          (reproduced from below)   #     SR Disr monoposony effect: marg effect on Price ($/BBL)
        MCdis_vul_dGDP_k            (reproduced from below)   #     SR Disr marginal effect on GDP loss ($/BBL)
        MCdis_vul_dDWL_k            (reproduced from below)   #     SR Disr marginal effect on DWL ($/BBL)
        MCdis_vul_dFC_k             (reproduced from below)   #     SR Disr marginal effect on Foreign Claims ($/BBL)
        MCdis_vul_deGDP_k           (reproduced from below)   #     SR Disr marginal effect: demand on GDP sensitivity ($/BBL)
      MCdis_vul_k                   (reproduced from below)   #   SR Dist marg effect on vulnerability costs ($/BBL)
        MCdis_size_dSSdDWL_k        (reproduced from below)   #     SR Disr marg effect of size on DWL ($/BBL)
        MCdis_size_dFC_k            (reproduced from below)   #     SR Disr marg effect of size on Foreign Claims ($/BBL)
        MCdis_size_dGNPdDelP_k      (reproduced from below)   #     SR Disr marg effect of size on GDP loss ($/BBL)
      MCdis_size_k                  (reproduced from below)   #   SR Disr marg effect of size on vuln costs ($/BBL)
    T_0                             (reproduced from below)   # Implicit tariff ($/BBL)
    EDelP_0                         (reproduced from below)   # Expected disr price increase ($/BBL)
    P_d0                            (reproduced from below)   # Domestic Price ($/BBL)
    q_d0                            (reproduced from below)   # Demand, Oil (MMBD)
    q_s0                            (reproduced from below)   # Supply (MMBD)
    q_i0                            (reproduced from below)   # Imports (MMBD)
    q_n0                            (reproduced from below)   # Demand, oil subst                                                 (MMBD-oilEqui)
    """

    # ======================================================================
    # FINAL CALCULATIONS - Current Case
    """
    Base                               #                                                                   (            )
    VarName                         Equation Notes   # Results                                                           (Units       )
    P_i0                            P_ik   # Opt Import price ($/BBL)
      MCmonopsony_k                 MCmonopsony = dP_i_dq_i*q_ik/w_k   #   Monopsony Premium ($/BBL)
      MCbop_k                       =MCbop = P_ik *n_pe  *n_eqk /w_k   #   BOP Premium ($/BBL)
      MCinf_k                       0  #   Inf Premium ($/BBL)
      MClr_pot_k                    MClr_pot = 0 (included in price, since Marg Ben of import consumption = GDP contribution)   #   LR Potential Output Premium ($/BBL)
    MCLR_k                          MCLR = MCmonopsony + MCbop + MCinf + MClr_pot   # Dependency (Long-run) Premium ($/BBL)
      E_MCdis_SS_k                    MCdis_SS =  MCdis_vul_dDWL +  MCdis_size_dSSdDWL   #   SR Disruption DWL Premium ($/BBL)
      E_MCdis_FC_k                    MCdis_FC =  MCdis_vul_monops +   MCdis_vul_dFC +   MCdis_size_dFC   #   SR Disruption Foreign-Claims Premium ($/BBL)
      E_MCdis_GDP_k                   MCdis_GDP =  MCdis_vul_dGDP +  MCdis_size_dGNPdDelP   #   SR Disruption GDP Dislocation Premium ($/BBL)
    E_MCdis_k                       MCdis_k = (MCdis_vul_k + MCdis_size_k)  = (MCdis_SS_k + MCdis_FC_k + MCdis_GDP_k)   # Security Premium ($/BBL)
    MCtot                           MCtot = (MCLR_k + MCdis_k)   # Total Premium ($/BBL)
        E_MCdis_vul_monops_k            E_MCdis_vul_monops_k = sum(j,Prob_Yj*MCdis_vul_monops_kj)/w_k   #     SR Disr monoposony effect: marg effect on Price ($/BBL)
        E_MCdis_vul_dGDP_k              E_MCdis_vul_dGDP_k = sum(j,Prob_Yj*MCdis_vul_dGDP_kj)/w_k   #     SR Disr marginal effect on GDP loss ($/BBL)
        E_MCdis_vul_dDWL_k              E_MCdis_vul_dDWL_k = sum(j,Prob_Yj*MCdis_vul_dDWL_kj)/w_k   #     SR Disr marginal effect on DWL ($/BBL)
        E_MCdis_vul_dFC_k               E_MCdis_vul_dFC_k = sum(j,Prob_Yj*MCdis_vul_dFC_kj)/w_k   #     SR Disr marginal effect on Foreign Claims ($/BBL)
        E_MCdis_vul_deGDP_k             E_MCdis_vul_deGDP_k = EDelP_k*(u_gdp/sigma_oUS_k) [times RhoD] ($/BBL)
      E_MCdis_vul_k                   E_MCdis_vul_k =     E_MCdis_vul_monops_k +     E_MCdis_vul_dGDP_k +     E_MCdis_vul_dDWL_k +     E_MCdis_vul_dFC_k   #   SR Dist marg effect on vulnerability costs ($/BBL)
        E_MCdis_size_dSSdDWL_k          E_MCdis_size_dSSdDWL_k = Sum(j, Prob_Yj*MCdis_size_dSSdDWL_kj)/w_k   #     SR Disr marg effect of size on DWL ($/BBL)
        E_MCdis_size_dFC_k              E_MCdis_size_dFC_k = Sum(j, Prob_Yj*MCdis_size_dFC_kj)/w_k   #     SR Disr marg effect of size on Foreign Claims ($/BBL)
        E_MCdis_size_dGNPdDelP_k        E_MCdis_size_dGNPdDelP_k = Sum(j, Prob_Yj*MCdis_size_dGNPdDelP_kj)/w_k   #     SR Disr marg effect of size on GDP loss ($/BBL)
      E_MCdis_size_k                  E_E_MCdis_size_k = E_E_MCdis_size_dSSdDWL_k + E_E_MCdis_size_dFC_k +  E_E_MCdis_size_k_dGNPdDelP_k   #   SR Disr marg effect of size on vuln costs ($/BBL)
    T_0                             T_1 (from above), T_0 = P_d0 - Pi0, T_1 refers to T_1 elsewhere   # Implicit tariff ($/BBL)
    EDelP_0                         EDelP_k = sum(j, PrDeltaP_kj)   # Expected disruption price increase ($/BBL)
    P_d0                            P_d1=P_i1+T_1, P_d0   # Domestic Price ($/BBL)
    q_d0                            q_d1 = $q_d0*($P_d1/$P_d0)^$n_dlr, and q_d0 = $q_d0*(P_d0_calced/$P_d0)^$n_dlr   # Demand, Oil (MMBD)
    q_s0                            q_s1 = $q_s0+($P_d1-$P_d0)*(d_qS/d_Pd) (note linear approx), and q_s0 = $q_s0*(P_d0_calced/$P_d0)^$n_slr   # Supply (MMBD)
    q_i0                            q_ik = d_dk - q_sk   # Imports (MMBD)
    q_n0                            q_nk = =$q_n0*($P_dk/$P_d0)^$n_nlr   # Demand, oil subst (MMBD)
                                       #                                                                   (            )
                                       # Cost of Free Market Policy ($mill/day)                            (            )
                                       #                                                                   (            )
                                       #                                                                   (            )
    """

    EDelP_k = np.sum(PrDeltaP_kj, 0)  # Expected disruption price increase ($/BBL)
    E_MCdis_vul_monops_k = (
        np.sum(Prob_Yj * MCdis_vul_monops_kj, 0) / w_k
    )  #     SR Disr monoposony effect: marg effect on Price ($/BBL)
    E_MCdis_vul_dGDP_k = (
        np.sum(Prob_Yj * MCdis_vul_dGDP_kj, 0) / w_k
    )  #     SR Disr marginal effect on GDP loss ($/BBL)
    E_MCdis_vul_dDWL_k = (
        np.sum(Prob_Yj * MCdis_vul_dDWL_kj, 0) / w_k
    )  #     SR Disr marginal effect on DWL ($/BBL)
    E_MCdis_vul_dFC_k = (
        np.sum(Prob_Yj * MCdis_vul_dFC_kj, 0) / w_k
    )  #     SR Disr marginal effect on Foreign Claims ($/BBL)
    E_MCdis_vul_deGDP_k = EDelP_k * (
        u_gdp / sigma_oUS_k
    )  #     SR Disr marginal effect: demand on GDP sensitivity [times RhoD] ($/BBL)
    E_MCdis_vul_k = (
        E_MCdis_vul_monops_k
        + E_MCdis_vul_dGDP_k
        + E_MCdis_vul_dDWL_k
        + E_MCdis_vul_dFC_k
    )  #   SR Dist marg effect on vulnerability costs ($/BBL)
    E_MCdis_size_dSSdDWL_k = (
        np.sum(Prob_Yj * MCdis_size_dSSdDWL_kj, 0) / w_k
    )  #     SR Disr marg effect of size on DWL ($/BBL)
    E_MCdis_size_dFC_k = (
        np.sum(Prob_Yj * MCdis_size_dFC_kj, 0) / w_k
    )  #     SR Disr marg effect of size on Foreign Claims ($/BBL)
    E_MCdis_size_dGNPdDelP_k = (
        np.sum(Prob_Yj * MCdis_size_dGNPdDelP_kj, 0) / w_k
    )  #     SR Disr marg effect of size on GDP loss ($/BBL)
    E_MCdis_size_k = (
        E_MCdis_size_dSSdDWL_k + E_MCdis_size_dFC_k + E_MCdis_size_dGNPdDelP_k
    )  #   SR Disr marg effect of size on vuln costs ($/BBL)
    MCmonopsony_k = dP_i_dq_i * q_ik / w_k  #   Monopsony Premium ($/BBL)
    MCbop_k = P_ik * n_pe * n_eqk / w_k  #   BOP Premium ($/BBL)
    MCinf_k = 0  #   Infl Premium ($/BBL)
    MClr_pot_k = 0.0  # (included in price, since Marg Ben of import consumption = GDP contribution)   #   LR Potential Output Premium ($/BBL)
    MCLR_k = (
        MCmonopsony_k + MCbop_k + MCinf_k + MClr_pot_k
    )  # Dependency (Long-run) Premium ($/BBL)
    E_MCdis_SS_k = (
        E_MCdis_vul_dDWL_k + E_MCdis_size_dSSdDWL_k
    )  #   SR Disruption DWL Premium ($/BBL)
    E_MCdis_FC_k = (
        E_MCdis_vul_monops_k + E_MCdis_vul_dFC_k + E_MCdis_size_dFC_k
    )  #   SR Disruption Foreign-Claims Premium ($/BBL)
    E_MCdis_GDP_k = (
        E_MCdis_vul_dGDP_k + E_MCdis_size_dGNPdDelP_k
    )  #   SR Disruption GDP Dislocation Premium ($/BBL)
    E_MCdis_k = (
        E_MCdis_vul_k + E_MCdis_size_k
    )  #  = (MCdis_SS_k + MCdis_FC_k + MCdis_GDP_k)   # Security Premium ($/BBL)
    MCtot_k = MCLR_k + E_MCdis_k  # Total Premium ($/BBL)
    # T_0                             T_1 (from above), T_0 = P_d0 - Pi0, T_1 refers to T_1 elsewhere   # Implicit tariff ($/BBL)

    # ======================================================================
    """
                                    Equation Notes   # Summary Results (outputs to track during @risk simulation:        (Units       )
    pi_m                            pi_m = MCLR_k   # MonopsonyPremium (Cartel Rent) ($/BBL)
    pi_di                           pi_di =     E_MCdis_vul_dFC_k +     E_MCdis_vul_monops_k +     E_MCdis_size_dFC_k   # Disruption: Increased Import Cost ($/BBL)
    pi_dm                           pi_dm =     E_MCdis_vul_dGDP_k +     E_MCdis_vul_dDWL_k +     E_MCdis_size_dSSdDWL_k +     E_MCdis_size_dGNPdDelP_k   # Disruption: Macro Adj Cost ($/BBL)
    pi_d                            pi_d = pi_dm + pi_di   # Disruption: Total ($/BBL)
    pi                              pi = pi_m + pi_d   # Total        ($/BBL)
    dP_i_dq_i                       (reproduced from below)   # Diagnostic: Price Slope (($/bbl)/MMBD)
    dq_iNO_over_dq_iUS              =(q_DNonUS_1-q_DNonUS_0)/(q_i1-q_i0),  and (q_INonUS_1-q_INonUS_0)/(q_i1-q_i0)   # Diagnostic: NonUS Demand Takeback, Import Takeback (Percent)
    dq_sOPEC_over_dq_iUS            =(S_NO_1-S_NO_0)/(q_i1-q_i0) and (S_OPEC1-S_OPEC0)/(q_i1-q_i0)   # Diagnostic: NonUS Supply Takeback, OPEC Supply (Percent)
    e_SOPEC                         (reproduced from above)   # Elas:OPEC Supply (Unitless)
    e_SNetToUS_k                    (reproduced from above)   # Elas:Net Import Supply to US (Unitless)
    """

    # ======================================================================
    # Summary Results (outputs to track during @risk simulation:        (Units       ) Equation Notes

    # Summary Results (outputs to track during @risk simulation:        (Units       )
    pi_m = MCLR_k  # MonopsonyPremium (Cartel Rent) ($/BBL)
    pi_di = (
        E_MCdis_vul_dFC_k + E_MCdis_vul_monops_k + E_MCdis_size_dFC_k
    )  # Disruption: Increased Import Cost ($/BBL)
    pi_dm = (
        E_MCdis_vul_dGDP_k
        + E_MCdis_vul_dDWL_k
        + E_MCdis_size_dSSdDWL_k
        + E_MCdis_size_dGNPdDelP_k
    )  # Disruption: Macro Adj Cost ($/BBL)
    pi_d = pi_dm + pi_di  # Disruption: Total ($/BBL)
    pi_tot = pi_m + pi_d  # Total        ($/BBL)
    # dP_i_dq_i                       (reproduced from below)   # Diagnostic: Price Slope (($/bbl)/MMBD)

    # dq_iNO_over_dq_iUS      = (q_DNonUS_1-q_DNonUS_0)/(q_i1-q_i0)  # and (q_INonUS_1-q_INonUS_0)/(q_i1-q_i0)   # Diagnostic: NonUS Demand Takeback, Import Takeback (Percent)
    # dq_sOPEC_over_dq_iUS    = (S_NO_1-S_NO_0)/(q_i1-q_i0)         # and (S_OPEC1-S_OPEC0)/(q_i1-q_i0)   # Diagnostic: NonUS Supply Takeback, OPEC Supply (Percent)

    # e_SOPEC                         (reproduced from above)   # Elas:OPEC Supply (Unitless)
    # e_SNetToUS_k                    (reproduced from above)   # Elas:Net Import Supply to US (Unitless)
    pi_components = [
        pi_tot,
        pi_m,
        pi_di,
        pi_dm,
        pi_d,
        E_MCdis_vul_monops_k,
        E_MCdis_vul_dGDP_k,
        E_MCdis_vul_dDWL_k,
        E_MCdis_vul_dFC_k,
        E_MCdis_vul_deGDP_k,
        E_MCdis_size_dSSdDWL_k,
        E_MCdis_size_dFC_k,
        E_MCdis_size_dGNPdDelP_k,
        MCmonopsony_k,
    ]

    if debug or np.isnan(pi_tot):
        print("P_i0", P_i0)
        print("q_i0", q_i0)
        print("q_INonUS_0", q_INonUS_0)
        print("S_OPEC", S_OPEC)

        print("n_dlr", n_dlr)
        print("e_DNO", e_DNO)
        print("e_INonUS", e_INonUS)
        print("e_SOPEC", e_SOPEC)
        print("e_SNetToUS_0", e_SNetToUS_0)

        print("dP_i_dq_i", dP_i_dq_i)
        print("MCmonopsony_k", MCmonopsony_k)
        print("w_k", w_k)
        print("Prob_Yj", Prob_Yj)
        print("w_kj", w_kj)
        print("dQ_tdq_i_kj", dQ_tdq_i_kj)
        print("dQ_udq_i_kj", dQ_udq_i_kj)
        print("dQ_t_dq_ik", dQ_t_dq_ik)
        print("u_gdp", u_gdp)
        print("DeltaP_kj", DeltaP_kj)
        print("P_dk", P_dk)
        print("dP_ddq_ik", dP_ddq_ik)

    return pi_components


# ======================================================================


# %%
"""
#                                                                   (            )
                                   #                                                                   (            )
                                   #                                                                   (            )
                                   #                                                                   (            )
                                   #                                                                   (            )
                                   #                                                                   (            )
                                   #                                                                   (            )
                                   #                                                                   (            )
                                   #                                                                   (            )
                                Equation Notes   # SOLUTION CONVERGENCE INDICATORS                                   (Units       )
0 if Mkt Balance:               MktBalance = ABS(q_d1-q_s1-q_i1)   # Excess Import Demand (MMBD)
0 if Opt Tax/Prem (ConvTest):   ConvTest = ABS(T_1-PREM_1)   # Implicit Tariff Minus Premium ($/BBL)
0 if Free Market:               ABS(T_1)   # Implicit Tariff ($/BBL)
                                   #                                                                   (            )
-                                  # -                                                                 (            )
                                   # Solver Models:                                                    (            )
                                   #                                                                   (            )
                                   #                                                                   (            )
                                   #                                                                   (            )
                                   #                                                                   (            )
                                   #                                                                   (            )
-                                  # -                                                                 (            )
                                   # Math Program (Solver Instructions)                                (            )
ConvTest = ABS(T_1-PREM_1)      ConvTest = ABS(T_1-PREM_1)   # Minimize:                                                         (            )
P_d1                            P_d1   # By changing:                                                      (            )
P_i1, P_d1, q_d1, q_s1 >= 0.01  P_i1, P_d1, q_d1, q_s1 >= 0.01   # Subject to:                                                       (            )
T_1 > 0.0                       T_1 > 0.0   #                                                                   (            )
                                   #                                                                   (            )
                                   #                                                                   (            )
                                   #                                                                   (            )
                                   #                                                                   (            )
                                   # OTHER INPUTS: Disruption Sizes, Probability Cases (selectors are  (            )
                                   #                                                                   (            )
                                   #                                                                   (            )
L_disr                         Disruption Length, years   # Duration (Disruption Length, Years)                               (            )
                                   #                                                                   (            )
                                Disr Size, MMBD   # Disr Size, MMBD                                                   (            )
Case0                           - exog - Decade Probs   # W0        (Unitless)
Case1                           - exog - Decade Probs   # W1        (Unitless)
Case2                           - exog - Decade Probs   # W2        (Unitless)
Case3                           - exog - Decade Probs   # W3        (Unitless)
CaseDOE90                       - exog - Decade/Annual? Probs   # DOE90 Midcase (annual?) (Unitless)
CaseEMF2005                     - exog - Decade Probs   # EMF2005 Midcase (test) (Unitless)
                                World View Choice   # ProbSelector:                                                     (            )
                                Selected Decade Probs   #                                                                   (            )
                                Selected Annual Probs   #                                                                   (            )
                                   #                                                                   (            )
                                   #                                                                   (            )
                                   #                                                                   (            )
                                   #                                                                   (            )
                                   #                                                                   (            )
"""


# %%
# Following UNUSED (parameters set near beginning of eval_one_case)
# Todo: Some following are valid for k in {0,1}, others must be differentiated

# Variables - Reference (non-Opt import level) values
def calcBaseVars():
    global q_d0, q_s0, S_OPEC, S_tot, q_INonUS_0  # inputs
    global P_d0, q_i0, T_0, S_NO, S_iToUS_0, q_DNonUS  # altered by this procedure
    P_d0 = P_i0  # domestic oil price (P_d1 chosen by solver) ($/BBL)
    q_i0 = q_d0 - q_s0  # oil import level (q_ik same formula)(MMBD)
    T_0 = (
        P_d0 - P_i0
    )  # T_k = P_dk - P_ik, but T_0 = 0 and Unused, T_1 = P_d1 - P_i1 determined by solver choice of P_d1   # Implicit tariff ($/BBL)
    S_NO = S_tot - S_OPEC - q_s0  # Other NonOPEC Supply <-Unused-> (MMBD)
    #   S_NO_0 = S_tot - S_OPEC - q_s0
    #   S_NO_1 = S_NO_0*(P_i1/P_i1)**e_SNO
    S_iToUS_0 = (
        S_OPEC - q_INonUS_0
    )  # Net Import Supply to US  (Need to subtract OPEC demand) <-Unused->(MMBD)
    #   S_iToUS_0 = S_OPEC - q_INonUS_0               # Net Import Supply to US  (Need to subtract OPEC demand) <-Unused->(MMBD)
    #   S_iToUS_1 = S_iToUS_0*(P_i1/P_i0)**e_SNetToUS_0  # Net Import Supply to US (MMBD)
    q_DNonUS_0 = q_INonUS_0 + S_NO_0  # Other NonOPEC Demand (MMBD)
    #   q_DNonUS_1 = q_DNonUS_0*(P_i1/P_i0)**e_DNO     # Other NonOPEC Demand (MMBD)
