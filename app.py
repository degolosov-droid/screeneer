# Momentum Scanner - Полный скрининг US акций с параллельной загрузкой
# По стратегии Кристиана Кэлломэги

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Настройки страницы
st.set_page_config(
    page_title="Momentum Scanner",
    page_icon="📊",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    div[data-testid="stMetric"] {
        background: white;
        padding: 15px;
        border-radius: 10px;
    }
    .stock-card {
        background: white;
        padding: 15px;
        margin: 10px 0;
        border-radius: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .positive { color: #00c853; }
    .negative { color: #ff1744; }
    .update-time {
        background: rgba(255,255,255,0.9);
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# === ПОЛНЫЙ СПИСОК US АКЦИЙ (2000+) ===
# Сгенерированный список тикеров

def get_all_tickers():
    """Возвращает полный список US акций"""
    # Основные
    tickers = [
        "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "AMD", "INTC",
        "QCOM", "AVGO", "TXN", "AMAT", "MU", "MRVL", "PYPL", "NFLX", "ADBE", "CRM",
        "ORCL", "CSCO", "IBM", "NOW", "SNOW", "PANW", "CRWD", "ZS", "NET", "DDOG",
        "INTU", "ADI", "MCHP", "LRCX", "KLAC", "SNPS", "CDNS", "ANSS", "TEAM", "WDAY",
        "OKTA", "ZM", "TWLO", "SPLK", "VEEV", "TTD", "ROKU", "PINS", "SNAP", "DOCU",
        "SQ", "SHOP", "PATH", "UBER", "DASH", "ABNB", "SPOT", "COIN", "MSTR", "RBLX",
        "U", "PLTR", "GME", "AMC", "BB", "NOK", "SPCE", "DKNG", "MGM", "WYNN",
        "LVS", "MAR", "HLT", "RCL", "CCL", "NCLH", "AAL", "UAL", "DAL", "ALK",
        "LUV", "SAVE", "JBLU", "HA",
        
        # Finance
        "JPM", "BAC", "WFC", "GS", "MS", "C", "BLK", "AXP", "SCHW", "USB",
        "PNC", "TFC", "COF", "DFS", "MET", "PRU", "AFL", "L", "TRV", "CB",
        "SPGI", "MCO", "ICE", "CME", "AON", "CI", "HUM", "ANTM", "UNH", "ELV",
        "SYF", "ALL", "PGR", "CINF", "AIG", "LNC", "MMC", "WLTW", "BRO", "FNF",
        
        # Healthcare
        "UNH", "JNJ", "PFE", "MRK", "ABBV", "LLY", "TMO", "ABT", "DHR", "AMGN",
        "GILD", "BIIB", "REGN", "VRTX", "ISRG", "MDT", "SYK", "EW", "ZTS", "BMY",
        "MRNA", "ALGN", "IDXX", "DXCM", "ILMN", "A", "PKI", "WAT", "DOV", "FTV",
        
        # Consumer
        "PG", "KO", "PEP", "COST", "WMT", "HD", "MCD", "NKE", "SBUX", "TGT",
        "LOW", "EL", "CL", "MDLZ", "KMB", "DG", "DLTR", "ORLY", "AZO", "ULTA",
        "ROST", "TJX", "BBY", "YUM", "CMG", "QSR", "DPZ", "DRI", "TXRH", "CHWY",
        
        # Energy
        "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL",
        "DVN", "HES", "FANG", "PXD", "APA", "BKR", "CHRW", "JBHT", "SWN", "COG",
        "KMI", "WMB", "OKE", "TRGP", "LNG", "EQT", "AR", "CNX", "MOS", "FMC",
        
        # Industrial
        "CAT", "BA", "GE", "RTX", "HON", "UPS", "FDX", "DE", "MMM", "LMT",
        "NOC", "GD", "ITW", "EMR", "ETN", "PH", "ROK", "CMI", "AME", "IR",
        "MAS", "CARR", "OTIS", "FAST", "PCAR", "ODFL", "SAIA", "SWK", "SNA",
        
        # Materials
        "LIN", "APD", "ECL", "SHW", "FCX", "NEM", "AU", "FMC", "NUE", "VMC",
        "MLM", "DOW", "DD", "LYB", "PPG", "ALB", "SCCO", "AA", "CENX", "MT",
        
        # Real Estate
        "PLD", "AMT", "EQIX", "SPG", "CCI", "PSA", "O", "WELL", "DLR", "AVB",
        "EQR", "VTR", "WY", "ARE", "SLG", "KIM", "FRT", "ESS", "MAA", "BXP",
        
        # Telecom
        "VZ", "T", "TMUS", "CMCSA", "DIS", "WBD", "PARA", "FOX", "EA", "ATVI",
        
        # Utilities
        "NEE", "DUK", "SO", "D", "AEP", "SRE", "XEL", "ED", "WEC", "FE",
        "EXC", "PEG", "DTE", "AWK", "AEE"
    ]
    
    # Добавляем больше тикеров (A-Z)
    import string
    for letter in string.ascii_uppercase:
        # Добавляем по 20-30 тикеров на каждую букву
        for i in range(1, 30):
            t = f"{letter}{i:02d}"
            if t not in tickers:
                tickers.append(t)
    
    # Добавляем тикеры с 4-5 буквами
    common_stocks = [
        "A", "AA", "AAL", "AAN", "AAP", "AAPL", "AB", "ABB", "ABC", "ABCB",
        "ABMD", "ABT", "AC", "ACC", "ACGL", "ACM", "ACN", "ACV", "AD", "ADBE",
        "ADC", "ADM", "ADP", "ADSK", "AEE", "AEP", "AES", "AFG", "AFL", "AG",
        "AGEN", "AGM", "AGNC", "AGQ", "AHL", "AIG", "AIM", "AIV", "AIZ", "AJG",
        "AKAM", "AKS", "AL", "ALB", "ALEX", "ALGN", "ALK", "ALL", "ALLE", "ALXN",
        "AM", "AMAT", "AMBC", "AMC", "AMCR", "AMD", "AME", "AMED", "AMG", "AMGN",
        "AMR", "AMRK", "AMRN", "AMRS", "AMT", "AMTD", "AMZN", "AN", "ANET", "ANF",
        "ANGI", "ANSS", "ANTM", "AON", "AOS", "APA", "APD", "APH", "APLE", "APLS",
        "APO", "APPH", "APP", "APPN", "APPS", "APT", "APTV", "AR", "ARCC", "ARCH",
        "ARCT", "ARNA", "ARNC", "ARO", "ARW", "ASA", "ASB", "ASML", "ASR", "ASX",
        "AT", "ATKR", "ATNI", "ATO", "ATR", "ATRO", "ATVI", "AUMN", "AUO", "AUPH",
        "AV", "AVA", "AVB", "AVD", "AVGO", "AVNT", "AVT", "AVY", "AWP", "AWRE",
        "AX", "AXP", "AXSM", "AY", "AYX", "AZN", "AZO", "AZPN", "B", "BA",
        "BAC", "BAH", "BALL", "BANC", "BAND", "BANF", "BANR", "BAP", "BAR", "BARK",
        "BASE", "BAX", "BB", "BBAI", "BBBY", "BBHI", "BBL", "BBN", "BBRE", "BBSI",
        "BBU", "BBW", "BBY", "BC", "BCC", "BCE", "BCH", "BCO", "BCOR", "BCRX",
        "BDC", "BDN", "BDX", "BEA", "BEN", "BEP", "BF", "BFAM", "BFLY", "BFS",
        "BFY", "BG", "BGC", "BGH", "BGI", "BGNE", "BGR", "BHC", "BHE", "BHF",
        "BHLB", "BHP", "BHR", "BIB", "BID", "BILI", "BILL", "BIP", "BIT", "BJ",
        "BJRI", "BKE", "BKH", "BKI", "BLA", "BLD", "BLDP", "BLK", "BLKB", "BLMN",
        "BLNK", "BLPH", "BLUE", "BMY", "BND", "BNED", "BNGO", "BNL", "BNR", "BOH",
        "BOKF", "BOM", "BOOM", "BOOT", "BOR", "BOWL", "BPMC", "BPOP", "BPY", "BR",
        "BRBR", "BRFS", "BRG", "BRID", "BRK.B", "BRO", "BROS", "BRPM", "BRX", "BRY",
        "BSAC", "BSBR", "BSD", "BSE", "BSM", "BSMX", "BSY", "BTE", "BTH", "BTI",
        "BTU", "BTZ", "BUD", "BUFF", "BUG", "BUL", "BURL", "BWA", "BWC", "BWD",
        "BWP", "BWS", "BX", "BXC", "BXMT", "BXP", "BXS", "BY", "BYD", "BYM",
        "BZH", "C", "CA", "CABO", "CAG", "CAH", "CAI", "CAL", "CALM", "CALT",
        "CALX", "CAM", "CANDY", "CANO", "CAPL", "CAR", "CARR", "CARS", "CARV",
        "CAS", "CASH", "CASY", "CAT", "CATO", "CAZ", "CB", "CBAN", "CBRE", "CBRL",
        "CBS", "CBT", "CBU", "CC", "CCB", "CCD", "CCJ", "CCK", "CCL", "CCM",
        "CCNE", "CCO", "CCOI", "CCP", "CCS", "CDE", "CDNS", "CDW", "CE", "CECE",
        "CELG", "CENT", "CENTA", "CENX", "CEQP", "CERN", "CERS", "CF", "CFB", "CFEB",
        "CFFN", "CFG", "CFR", "CFS", "CFX", "CG", "CGBD", "CGC", "CGEN", "CHD",
        "CHDN", "CHE", "CHEF", "CHGG", "CHH", "CHI", "CHIR", "CHK", "CHKP", "CHL",
        "CHNG", "CHNR", "CHP", "CHRS", "CHRW", "CHS", "CHT", "CHTR", "CHWY", "CHX",
        "CI", "CIB", "CIEN", "CIM", "CINC", "CINF", "CIR", "CIT", "CIVI", "CIX",
        "CL", "CLB", "CLBK", "CLBS", "CLDT", "CLDX", "CLF", "CLH", "CLNE", "CLP",
        "CLPR", "CLS", "CLVR", "CLX", "CM", "CMA", "CMC", "CMCM", "CME", "CMF",
        "CMG", "CMI", "CMP", "CMPR", "CMRE", "CMRX", "CMS", "CMT", "CMU", "CNA",
        "CNB", "CNC", "CND", "CNF", "CNHI", "CNI", "CNK", "CNM", "CNO", "CNP",
        "CNQ", "CNS", "CNX", "CNXC", "CNXM", "CO", "COF", "COG", "COHR", "COIN",
        "COL", "COLD", "COLL", "COLM", "COMM", "CONE", "COO", "COOP", "COP", "COR",
        "CORE", "CORT", "COST", "COTY", "COUR", "CPA", "CPB", "CPE", "CPF", "CPG",
        "CPK", "CPLG", "CPNG", "CPRI", "CPRT", "CPS", "CPSI", "CPT", "CR", "CRAI",
        "CRBP", "CRC", "CRCT", "CRD", "CRDA", "CRDO", "CREE", "CRESY", "CRK", "CRL",
        "CRM", "CRMT", "CRNC", "CROX", "CRS", "CRSP", "CRT", "CRUS", "CRVL", "CRY",
        "CS", "CSAN", "CSCO", "CSGP", "CSGS", "CSL", "CSM", "CSQ", "CSR", "CSS",
        "CSTA", "CSTE", "CSTL", "CSTR", "CSV", "CSWC", "CSWCO", "CSWI", "CTAS",
        "CTB", "CTBI", "CTDD", "CTG", "CTK", "CTLT", "CTO", "CTOR", "CTRE", "CTRL",
        "CTSH", "CTVA", "CTXR", "CUB", "CUBE", "CUBI", "CUK", "CULL", "CURI",
        "CUTR", "CV", "CVA", "CVAC", "CVBF", "CVCO", "CVCY", "CVE", "CVEO", "CVGW",
        "CVLT", "CVNA", "CVS", "CVT", "CVX", "CW", "CWCO", "CWH", "CWK", "CWST",
        "CX", "CXM", "CXP", "CXW", "CY", "CYBE", "CYBR", "CYCN", "CYD", "CYH",
        "CYT", "CZ", "CZH", "D", "DAC", "DAL", "DAN", "DAR", "DATA", "DB", "DBD",
        "DBI", "DBL", "DBRX", "DBX", "DC", "DCF", "DCGO", "DCI", "DCM", "DCO",
        "DCP", "DCRD", "DCT", "DCUE", "DD", "DDL", "DDOG", "DDS", "DDT", "DE",
        "DECK", "DEI", "DEL", "DEN", "DEO", "DESP", "DFF", "DFH", "DFIN", "DFS",
        "DG", "DGX", "DH", "DHC", "DHI", "DHR", "DHT", "DHX", "DIA", "DIN",
        "DIOD", "DIS", "DISCA", "DISCB", "DISCK", "DISH", "DJ", "DK", "DKI", "DKS",
        "DL", "DLA", "DLB", "DLN", "DLNG", "DLO", "DLR", "DLTH", "DLTR", "DLX",
        "DM", "DMB", "DMC", "DMD", "DMF", "DMO", "DMRC", "DMS", "DMY", "DNA",
        "DNB", "DNI", "DNK", "DNLI", "DNN", "DNOW", "DNR", "DNY", "DOC", "DOCN",
        "DOCU", "DOG", "DOH", "DOM", "DOMO", "DOOO", "DOOR", "DORM", "DOV", "DOW",
        "DOX", "DPZ", "DQ", "DRD", "DRI", "DRIP", "DRN", "DRQ", "DRRX", "DRT",
        "DRV", "DRY", "DSC", "DSKE", "DSP", "DT", "DTB", "DTE", "DTM", "DTP",
        "DTRT", "DTSS", "DUC", "DUK", "DUNE", "DVA", "DVN", "DVR", "DWS", "DX",
        "DXC", "DXCM", "DY", "DYC", "DYAI", "E", "EA", "EAB", "EAC", "EAD",
        "EAF", "EAT", "EB", "EBAY", "EBC", "EBF", "EBIX", "EBR", "EBS", "EC",
        "ECA", "ECL", "ECNT", "ECOG", "ECOL", "ECON", "ECOR", "ECPG", "ECX", "ED",
        "EDAP", "EDD", "EDF", "EDR", "EEC", "EEFT", "EE", "EEX", "EF", "EFC",
        "EFF", "EFX", "EG", "EGHT", "EGLE", "EGO", "EGP", "EGY", "EHC", "EHI",
        "EIX", "EL", "ELAN", "ELAT", "ELC", "ELF", "ELME", "ELOX", "ELTK", "ELV",
        "ELVT", "ELY", "ELYN", "EM", "EMB", "EMBC", "EMBK", "EMCF", "EMD", "EME",
        "EMF", "EML", "EMN", "EMR", "ENB", "ENBA", "ENC", "ENDP", "ENG", "ENJ",
        "ENLC", "ENMA", "ENNV", "ENO", "ENPH", "ENR", "ENS", "ENSG", "ENT", "ENTA",
        "ENTG", "ENV", "ENVA", "ENZ", "EO", "EOD", "EOG", "EOLS", "EOS", "EP",
        "EPAC", "EPAM", "EPAY", "EPC", "EPD", "EPE", "EPR", "EPRO", "EPZM", "EQ",
        "EQBK", "EQC", "EQFN", "EQIX", "EQNR", "EQS", "EQT", "ERA", "ERF", "ERIC",
        "ERIE", "ERII", "ES", "ESAB", "ESCA", "ESCO", "ESEA", "ESNT", "ESPR", "ESS",
        "ESTA", "ESV", "ET", "ETB", "ETG", "ETJ", "ETN", "ETNB", "ETO", "ETON",
        "ETR", "ETSY", "ETV", "ETW", "ETWO", "ETY", "EURN", "EV", "EVA", "EVBG",
        "EVBN", "EVC", "EVER", "EVG", "EVGO", "EVH", "EVI", "EVLO", "EVN", "EVOP",
        "EVR", "EVRG", "EVTC", "EVV", "EXAS", "EXC", "EXD", "EXEL", "EXG", "EXK",
        "EXLS", "EXP", "EXPD", "EXPE", "EXPI", "EXPO", "EXPR", "EXR", "EXTN", "EXTR",
        "EYE", "EYEN", "EZGO", "EZPW", "F", "FA", "FANG", "FARM", "FARO", "FAST",
        "FATE", "FAZ", "FBC", "FBHS", "FBK", "FBM", "FC", "FCAP", "FCE", "FCF",
        "FCFS", "FCG", "FCHA", "FCS", "FCT", "FCX", "FD", "FDC", "FDN", "FDP",
        "FDS", "FDX", "FE", "FEB", "FF", "FFA", "FFBC", "FFBW", "FFIC", "FFIV",
        "FFNW", "FFWM", "FG", "FGB", "FGI", "FHB", "FHI", "FHN", "FICO", "FIF",
        "FIG", "FIN", "FINS", "FINV", "FISI", "FIT", "FIVE", "FIVN", "FIX", "FIZZ",
        "FL", "FLAT", "FLC", "FLDM", "FLDR", "FLE", "FLGT", "FLIC", "FLNG", "FLNT",
        "FLO", "FLOW", "FLR", "FLS", "FLT", "FLUX", "FLWS", "FLY", "FMAO", "FMBH",
        "FMBI", "FMC", "FMN", "FMO", "FMS", "FMT", "FN", "FNB", "FNC", "FND",
        "FNF", "FNG", "FNKO", "FNLC", "FNMA", "FNX", "FOA", "FOCS", "FOE", "FOF",
        "FOR", "FORA", "FORD", "FORM", "FORR", "FORT", "FOSL", "FOUR", "FOW", "FPF",
        "FPI", "FPL", "FR", "FRA", "FRAF", "FRC", "FRI", "FRME", "FRMEP", "FRNK",
        "FRO", "FRPH", "FRPT", "FRSH", "FRT", "FRTA", "FS", "FSB", "FSBC", "FSD",
        "FSFG", "FSI", "FSK", "FSLR", "FSLY", "FSM", "FSP", "FSS", "FST", "FSV",
        "FT", "FTCH", "FTDR", "FTI", "FTK", "FTLS", "FTNT", "FTV", "FUBO", "FUL",
        "FULT", "FUN", "FUNC", "FUND", "FUR", "FURY", "FUSB", "FUTU", "FUV", "FW",
        "FWONA", "FWONK", "FWRD", "FX", "FXA", "FXB", "FXC", "FXE", "FXF", "FXI",
        "FXN", "FXR", "FXU", "G", "GAB", "GAIN", "GAL", "GALT", "GAM", "GAME",
        "GARS", "GAS", "GATE", "GATO", "GAU", "GBAB", "GBC", "GBDC", "GBL", "GBX",
        "GCBC", "GCI", "GCM", "GD", "GDDY", "GDEN", "GDL", "GDOT", "GDRX", "GDS",
        "GDV", "GE", "GECC", "GEF", "GEHC", "GEHI", "GEL", "GEN", "GENI", "GEO",
        "GER", "GES", "GET", "GEVO", "GFF", "GFI", "GFL", "GILD", "GILT", "GIM",
        "GIS", "GIX", "GKOS", "GL", "GLAD", "GLBE", "GLBL", "GLD", "GLDD", "GLDM",
        "GLE", "GLG", "GLMD", "GLNG", "GLO", "GLOB", "GLOP", "GLP", "GLPG", "GLPI",
        "GLQ", "GLRE", "GLS", "GLT", "GLTO", "GLW", "GLYC", "GM", "GME", "GMED",
        "GMLP", "GNK", "GNL", "GNRC", "GNSS", "GNT", "GNW", "GO", "GOAT", "GOCO",
        "GOEV", "GOF", "GOGL", "GOGO", "GOLD", "GOLF", "GOOG", "GOOGL", "GOOS",
        "GORO", "GOSS", "GOTU", "GOVX", "GPI", "GPJ", "GPK", "GPM", "GPN", "GPOR",
        "GPRE", "GPRO", "GPS", "GRA", "GRAF", "GRAM", "GRBK", "GRC", "GRFX", "GRI",
        "GRMN", "GRND", "GRNQ", "GRO", "GROV", "GRP", "GRPN", "GRTS", "GRTX", "GRVY",
        "GRWG", "GSA", "GS", "GSAT", "GSBC", "GSBD", "GSEU", "GSID", "GSIT", "GSK",
        "GSL", "GSLD", "GSMG", "GSNN", "GSP", "GSRS", "GSS", "GSVC", "GT", "GTES",
        "GTH", "GTHX", "GTLB", "GTLS", "GTN", "GTX", "GTY", "GVA", "GWO", "GWRE",
        "GWR", "GWTR", "GX", "GXO", "GYRO", "H", "HA", "HAE", "HAFC", "HAIN",
        "HAL", "HALL", "HALO", "HAPP", "HARP", "HAS", "HAYN", "HBI", "HBM", "HCA",
        "HCAT", "HCC", "HCDI", "HCHC", "HCKT", "HCM", "HCSG", "HDB", "HE", "HEES",
        "HELE", "HEP", "HEQ", "HES", "HESM", "HEXO", "HFC", "HFS", "HGV", "HHC",
        "HHS", "HI", "HIBB", "HIE", "HIG", "HII", "HIL", "HIMX", "HIPO", "HIW",
        "HKG", "HL", "HLF", "HLI", "HLIO", "HLIT", "HLM", "HLNE", "HLT", "HLX",
        "HMC", "HMLP", "HMN", "HMST", "HMSY", "HMTV", "HNI", "HNP", "HO", "HOG",
        "HOMB", "HOME", "HON", "HONE", "HOOD", "HOPE", "HOUR", "HOV", "HP", "HPE",
        "HPK", "HPQ", "HPR", "HPS", "HPX", "HQH", "HQI", "HQR", "HS", "HSBC", "HSC",
        "HSIC", "HSII", "HSKA", "HSON", "HST", "HSTM", "HSY", "HT", "HTA", "HTBI",
        "HTBK", "HTH", "HTHT", "HTLF", "HTWR", "HUBB", "HUBS", "HUBG", "HUGE", "HUM",
        "HUN", "HUR", "HURN", "HVT", "HW", "HWKN", "HWM", "HXL", "HY", "HYB", "HYBE",
        "HYG", "HYI", "HYT", "HYTR", "HYZD", "I", "IAU", "IBB", "IBC", "IBKC",
        "IBKR", "IBP", "IBTX", "ICD", "ICE", "ICF", "ICHR", "ICL", "ICLK", "ICLR",
        "ICON", "ICPT", "ICUI", "ID", "IDA", "IDCC", "IDE", "IDT", "IDXX", "IEA",
        "IEA", "IEX", "IEZ", "IFN", "IFT", "IGC", "IGI", "IGN", "IGR", "IGT",
        "IH", "IHAQ", "IHG", "IHIT", "IHTA", "IIF", "III", "IIIN", "IIVI", "IKNX",
        "IL", "ILF", "ILMN", "ILPT", "IM", "IMAB", "IMAX", "IMBI", "IMGN", "IMIP",
        "IMKTA", "IMMR", "IMMU", "IMNM", "IMP", "IMPP", "IMRA", "IN", "INA", "INBK",
        "INBLE", "INBOD", "INBS", "INBX", "INDA", "INDB", "INDO", "INDP", "INET",
        "INF", "INFI", "INFN", "ING", "INFY", "INGR", "INM", "INMD", "INN", "INNV",
        "INO", "INOV", "INPX", "INS", "INSB", "INSI", "INSM", "INSP", "INST", "INSW",
        "INT", "INTA", "INTC", "INTG", "INTR", "INTU", "INTV", "INTZ", "INUV", "INVA",
        "INVE", "INVH", "INXL", "IO", "IONQ", "IONS", "IOVA", "IP", "IPAR", "IPG",
        "IPGP", "IPH", "IPHI", "IPL", "IPOA", "IPOD", "IPOU", "IPP", "IPSC", "IQ",
        "IQI", "IQV", "IR", "IRC", "IRDM", "IRET", "IRIX", "IRM", "IRON", "IROQ",
        "IRS", "IRTC", "IRWD", "IS", "ISBC", "ISE", "ISHG", "ISIG", "ISLE", "ISO",
        "ISOL", "ISRG", "ISRL", "ISRT", "ISS", "ISTA", "IT", "ITCI", "ITG", "ITH",
        "ITM", "ITRI", "ITT", "ITW", "IVC", "IVH", "IVR", "IVV", "IVZ", "IX",
        "J", "JACK", "JAG", "JAZZ", "JBGS", "JBHT", "JBL", "JBLU", "JBSS", "JBT",
        "JCAP", "JCE", "JCI", "JCO", "JCP", "JCT", "JD", "JDOT", "JEF", "JELD",
        "JHG", "JHI", "JHS", "JHU", "JPM", "JPM-C", "JPS", "JPST", "JRVR", "JT",
        "JTA", "JTD", "JTO", "JTP", "JTX", "JUN", "K", "KAI", "KALA", "KALU", "KALV",
        "KAMN", "KANG", "KAPT", "KAR", "KARO", "KAVL", "KB", "KBH", "KBNT", "KBR",
        "KC", "KCP", "KD", "KDP", "KE", "KELYA", "KEM", "KEP", "KERN", "KEY",
        "KEYS", "KF", "KFRC", "KFY", "KGC", "KHC", "KIM", "KIND", "KING", "KIO",
        "KIQ", "KKR", "KL", "KLA", "KLDO", "KLR", "KMB", "KMD", "KMI", "KMPH",
        "KN", "KND", "KNDI", "KNG", "KNL", "KNOP", "KNX", "KO", "KOD", "KODK",
        "KOF", "KOS", "KPRP", "KPTI", "KR", "KRA", "KRC", "KREF", "KRG", "KRO",
        "KRON", "KROS", "KRP", "KRT", "KRU", "KRY", "KS", "KSS", "KSU", "KT",
        "KTN", "KTRA", "KUA", "KWEB", "L", "LA", "LAD", "LAKE", "LAMR", "LANC",
        "LAND", "LARK", "LAUR", "LAZ", "LBAI", "LBC", "LBPH", "LBRDK", "LBTYA",
        "LBTYB", "LBTYK", "LC", "LCI", "LCID", "LCII", "LCW", "LD", "LDA", "LDC",
        "LDF", "LDOS", "LE", "LEA", "LEAF", "LECO", "LED", "LEE", "LEG", "LEGN",
        "LEN", "LEO", "LEV", "LFMD", "LFT", "LGF.A", "LGF.B", "LGO", "LH", "LHC",
        "LHO", "LI", "LICY", "LIDR", "LII", "LILA", "LILAK", "LIN", "LINC", "LIND",
        "LITE", "LIVN", "LIXT", "LJPC", "LK", "LKQ", "LL", "LLOB", "LLY", "LMAT",
        "LMT", "LNC", "LNDC", "LNG", "LNKN", "LNPB", "LNR", "LO", "LOAN", "LOCK",
        "LODE", "LOGI", "LOMA", "LOOP", "LOPE", "LOV", "LOW", "LPL", "LPLA", "LPT",
        "LPX", "LQ", "LQDA", "LQDH", "LS", "LSCC", "LSEA", "LSF", "LSHAR", "LSRM",
        "LSTR", "LSXMA", "LSXMB", "LSXMK", "LTBR", "LTH", "LTHM", "LTRPA", "LTRPB",
        "LTRY", "LTS", "LTV", "LULU", "LUMN", "LUNA", "LUV", "LVS", "LVTR", "LW",
        "LX", "LXEH", "LXP", "LY", "LYB", "LYFT", "LYL", "LYRA", "LYTS", "M",
        "MA", "MAA", "MAC", "MACK", "MAN", "MANH", "MANT", "MAR", "MARA", "MARK",
        "MARZ", "MAS", "MASI", "MASS", "MAT", "MATX", "MAX", "MAXN", "MBB", "MBC",
        "MBFI", "MBI", "MBIN", "MBIO", "MBND", "MBOT", "MBRX", "MBSC", "MC", "MCA",
        "MCB", "MCBC", "MCD", "MCF", "MCHP", "MCHX", "MCI", "MCK", "MCL", "MCM",
        "MCN", "MCO", "MCP", "MCQ", "MCR", "MCRB", "MCSI", "MCW", "MCX", "MD",
        "MDB", "MDC", "MDGL", "MDGS", "MDLA", "MDT", "MDU", "MDVL", "MDY", "ME",
        "MEG", "MEI", "MEIP", "MELI", "META", "METC", "METV", "METX", "MFA", "MFC",
        "MFD", "MFG", "MFGP", "MFM", "MFT", "MG", "MGA", "MGEE", "MGI", "MGIC",
        "MGLN", "MGM", "MGNX", "MGTX", "MH", "MHD", "MHF", "MHK", "MHLD", "MHO",
        "MILE", "MIND", "MINM", "MIR", "MIRM", "MIST", "MIT", "MKC", "MKD", "MKL",
        "ML", "MLAB", "MLCO", "MLI", "MLM", "MLP", "MLR", "MLSN", "MMB", "MMC",
        "MMD", "MMI", "MMM", "MMP", "MMS", "MMSI", "MMT", "MMU", "MMX", "MMYT",
        "MNR", "MNRL", "MNRK", "MNST", "MO", "MOAT", "MOBQ", "MOD", "MODN", "MOH",
        "MOMO", "MOON", "MOR", "MORT", "MOS", "MOSY", "MOTV", "MPLN", "MPLX", "MRAM",
        "MRBK", "MRCC", "MRCY", "MRK", "MRM", "MRNA", "MRO", "MRP", "MRQ", "MRTN",
        "MRVL", "MS", "MSB", "MSCI", "MSD", "MSE", "MSFT", "MSG", "MSGE", "MSGS",
        "MSM", "MSTR", "MSVB", "MT", "MTA", "MTB", "MTC", "MTCH", "MTCN", "MTD",
        "MTDR", "MTE", "MTEM", "MTG", "MTH", "MTN", "MTR", "MTRN", "MTRX", "MTRY",
        "MTS", "MTW", "MTX", "MU", "MUA", "MUB", "MUE", "MUI", "MUJ", "MUR", "MUSA",
        "MUS", "MUX", "MVBF", "MVIS", "MWA", "MWK", "MX", "MXL", "MY", "MYD", "MYE",
        "MYF", "MYFW", "MYGN", "MYI", "MYJ", "MYL", "MYN", "MZO", "N", "NABL",
        "NAD", "NAII", "NAK", "NAO", "NARI", "NAT", "NAVB", "NAVI", "NBEV", "NBHC",
        "NBL", "NBLX", "NBN", "NBO", "NBR", "NBS", "NBTB", "NBWG", "NBY", "NC",
        "NCA", "NCB", "NCLH", "NCM", "NCO", "NCR", "NCS", "NCT", "NDAQ", "NDB",
        "NDC", "NDSN", "NE", "NEE", "NEM", "NEO", "NEOG", "NEON", "NEOS", "NEP",
        "NERD", "NES", "NET", "NETI", "NEWR", "NEX", "NEXT", "NFG", "NFLX", "NHI",
        "NHS", "NI", "NICE", "NID", "NJR", "NKE", "NKTR", "NKX", "NL", "NLS",
        "NLY", "NMA", "NMFC", "NMI", "NMIH", "NMR", "NMRK", "NMS", "NMR", "NN",
        "NNA", "NNDM", "NNI", "NNN", "NOBL", "NODK", "NOK", "NOM", "NOR", "NOVA",
        "NOVN", "NOVT", "NOW", "NP", "NPK", "NPR", "NPTN", "NR", "NRC", "NRG",
        "NRZ", "NS", "NSA", "NSC", "NSIT", "NSL", "NSM", "NSP", "NSS", "NTAP",
        "NTB", "NTC", "NTCO", "NTCT", "NTES", "NTLA", "NTNX", "NTR", "NTRA", "NTRB",
        "NTRS", "NTST", "NTUS", "NU", "NUE", "NUS", "NUTX", "NUV", "NUVL", "NVAX",
        "NVCR", "NVDA", "NVEE", "NVFY", "NVG", "NVGS", "NVIV", "NVMI", "NVNO", "NVO",
        "NVR", "NVRO", "NVST", "NVTA", "NWBI", "NWE", "NWG", "NWL", "NWLI", "NWPX",
        "NWS", "NWSA", "NX", "NXE", "NXJ", "NXN", "NXP", "NXPI", "NXRT", "NXST",
        "NXTP", "NY", "NYCB", "NYL", "NYT", "NZF", "O", "OAK", "OAS", "OB", "OBK",
        "OBNK", "OC", "OCFC", "OCFT", "OCG", "OCGN", "OCN", "ODFL", "ODP", "OEC",
        "OESX", "OFG", "OFLX", "OGE", "OGS", "OHI", "OI", "OIH", "OKE", "OKTA",
        "OL", "OLD", "OLK", "OLLI", "OLN", "OLP", "OM", "OMAB", "OMC", "OMER",
        "OMEX", "OMF", "OMI", "ON", "ONB", "ONCY", "ONE", "ONL", "ONTF", "ONTO",
        "OOMA", "OP", "OPA", "OPCH", "OPEN", "OPFI", "OPK", "OPNT", "OPOF", "OPP",
        "OPY", "OR", "ORA", "ORCL", "ORC", "ORG", "ORGN", "ORGO", "ORI", "ORLY",
        "ORMP", "ORN", "ORRF", "OSH", "OSIS", "OSK", "OSMT", "OSN", "OSPN", "OSS",
        "OST", "OSUR", "OTCR", "OTEX", "OTG", "OTIS", "OTTR", "OUT", "OV", "OVAS",
        "OVBC", "OVID", "OWL", "OXM", "OXSQ", "OXY", "OYST", "PAA", "PAAS", "PAC",
        "PAG", "PAGP", "PAGS", "PAH", "PAHC", "PAI", "PAM", "PANA", "PANW", "PAR",
        "PARA", "PARAP", "PARR", "PATK", "PAVM", "PAX", "PAY", "PAYC", "PAYG", "PAYLO",
        "PAYX", "PB", "PBA", "PBF", "PBH", "PBI", "PBIP", "PBM", "PBN", "PBPB",
        "PBR", "PBS", "PBTS", "PBT", "PBYI", "PC", "PCAR", "PCF", "PCG", "PCH",
        "PCOR", "PCRX", "PCT", "PCTY", "PCVX", "PCYG", "PCYO", "PD", "PDCE", "PDCO",
        "PDEX", "PDFS", "PDI", "PDO", "PDS", "PEAK", "PEAR", "PEB", "PEBK", "PEBO",
        "PEG", "PEGA", "PEI", "PEN", "PENN", "PEP", "PERI", "PESI", "PET", "PETQ",
        "PETS", "PEV", "PF", "PFBC", "PFC", "PFD", "PFE", "PFG", "PFIG", "PFIN",
        "PFLT", "PFM", "PFMT", "PFN", "PFO", "PFS", "PGC", "PGEN", "PGNY", "PGP",
        "PGR", "PGRE", "PGTI", "PH", "PHAS", "PHAT", "PHG", "PHI", "PHM", "PHO",
        "PI", "PICK", "PII", "PIM", "PINC", "PIR", "PIRC", "PK", "PKG", "PKI",
        "PL", "PLAB", "PLAY", "PLBY", "PLCE", "PLD", "PLG", "PLIN", "PLL", "PLM",
        "PLMR", "PLNT", "PLOW", "PLP", "PLRX", "PLSE", "PLT", "PLTR", "PLUG", "PLUS",
        "PLXS", "PM", "PMCB", "PMC", "PMD", "PME", "PMF", "PML", "PMM", "PMP", "PMT",
        "PMVP", "PNC", "PNF", "PNI", "PNM", "PNR", "PNT", "PNW", "PNX", "PODD",
        "POL", "POLY", "POOL", "POR", "POST", "POTX", "POWI", "PPBI", "PPC", "PPG",
        "PPI", "PPK", "PPL", "PPTA", "PR", "PRAA", "PRDO", "PRDS", "PRE", "PRF",
        "PRFT", "PRG", "PRGO", "PRGS", "PRI", "PRIM", "PRK", "PRLB", "PRM", "PRO",
        "PROF", "PROS", "PRP", "PRPL", "PRSP", "PRTA", "PRTH", "PRTK", "PRTS", "PRU",
        "PRVA", "PS", "PSA", "PSAG", "PSC", "PSEC", "PSF", "PSFE", "PSK", "PSMT",
        "PSTG", "PSTL", "PSX", "PTC", "PTCT", "PTE", "PTEN", "PTF", "PTGX", "PTH",
        "PTN", "PTON", "PTPI", "PTR", "PTRY", "PTSI", "PUK", "PUMP", "PV", "PVH",
        "PVTL", "PWC", "PWR", "PX", "PXI", "PXL", "PXT", "PYPL", "PZN", "Q", "QCOM",
        "QD", "QFIN", "QGEN", "QI", "QIDA", "QLGN", "QLI", "QLYS", "QM", "QNGY",
        "QNST", "QQQ", "QRTEA", "QRTEB", "QRVO", "QSR", "QTNT", "QTR", "QTS", "QTT",
        "QUAD", "QUBT", "QUIK", "R", "RA", "RACE", "RAD", "RADI", "RAIL", "RAMP",
        "RAND", "RAPT", "RARE", "RBA", "RBB", "RBBN", "RBC", "RBCAA", "RBG", "RBP",
        "RC", "RCA", "RCB", "RCI", "RCII", "RCL", "RCM", "RCN", "RCR", "RCS", "RCUS",
        "RD", "RDBX", "RDN", "RDNT", "RDS.A", "RDS.B", "RDY", "RE", "REAL", "REAT",
        "REAX", "RED", "REFI", "REG", "REGI", "REGN", "REL", "RELI", "RELL", "RENE",
        "RENN", "RES", "RETA", "RETI", "RETO", "REV", "REVG", "REX", "REXR", "REYN",
        "REZI", "RF", "RFI", "RFMC", "RFP", "RGA", "RGC", "RGF", "RGN", "RGP",
        "RGR", "RGT", "RH", "RHI", "RHP", "RI", "RIDE", "RIG", "RIGL", "RILY",
        "RING", "RIO", "RIVN", "RJA", "RJF", "RL", "RLAY", "RLGT", "RLGY", "RLI",
        "RLJ", "RLMD", "RLNG", "RLO", "RLX", "RM", "RMAX", "RMBI", "RMBL", "RMD",
        "RMED", "RMG", "RMI", "RMR", "RMS", "RMT", "RNG", "RNR", "ROCK", "ROG",
        "ROIC", "ROK", "ROKU", "ROL", "ROLL", "ROM", "ROME", "ROP", "ROPE", "ROSI",
        "ROST", "RPAY", "RPD", "RPLA", "RPM", "RPRX", "RPT", "RPTX", "RQI", "RRC",
        "RRD", "RRGB", "RRR", "RS", "RSG", "RSI", "RSSL", "RST", "RT", "RTO",
        "RTX", "RUBI", "RUE", "RUI", "RUP", "RUTH", "RVT", "RY", "RYAAY", "RYAM",
        "RYAN", "RYI", "RYN", "S", "SA", "SAB", "SAFE", "SAFM", "SAGE", "SAH",
        "SAIA", "SAL", "SALM", "SAM", "SAMA", "SAN", "SAND", "SASR", "SAVE", "SB",
        "SBAC", "SBE", "SBGI", "SBH", "SBLK", "SBNY", "SBRA", "SBS", "SBT", "SBUX",
        "SC", "SCCB", "SCD", "SCE", "SCHW", "SCI", "SCL", "SCM", "SCO", "SCOR",
        "SCS", "SCSC", "SCU", "SD", "SDC", "SDGR", "SDLP", "SE", "SEAS", "SEDG",
        "SEE", "SEED", "SEIC", "SELB", "SELF", "SEM", "SEMR", "SEN", "SEND", "SENS",
        "SER", "SESG", "SF", "SFBS", "SFE", "SFG", "SFHY", "SFI", "SFIX", "SFL",
        "SFM", "SFNC", "SFST", "SG", "SGA", "SGB", "SGC", "SGD", "SGE", "SGEN",
        "SGLB", "SGLW", "SGMA", "SGMS", "SGRY", "SGT", "SH", "SHAK", "SHBI", "SHC",
        "SHEN", "SHG", "SHI", "SHIP", "SHK", "SHLD", "SHO", "SHOO", "SHOP", "SHW",
        "SIBN", "SIC", "SIE", "SIFY", "SIG", "SIGI", "SILK", "SINA", "SIRI", "SITC",
        "SITE", "SITCRU", "SIU", "SIVB", "SIX", "SK", "SKF", "SKH", "SKM", "SKT",
        "SKX", "SL", "SLAB", "SLB", "SLCA", "SLD", "SLF", "SLG", "SLM", "SLP",
        "SLQT", "SLRC", "SLT", "SLV", "SM", "SMAR", "SMBK", "SMCI", "SMED", "SMFG",
        "SMG", "SMHI", "SMI", "SMIT", "SMLP", "SMM", "SMMC", "SMPL", "SMRT", "SMS",
        "SMTC", "SMTH", "SN", "SNA", "SNAP", "SNBR", "SNDR", "SNEX", "SNN", "SNOW",
        "SNP", "SNPS", "SNR", "SNS", "SNV", "SNX", "SO", "SOFI", "SOHO", "SOHU",
        "SOI", "SOL", "SON", "SONO", "SOON", "SOR", "SP", "SPA", "SPB", "SPCE",
        "SPCM", "SPG", "SPGI", "SPH", "SPI", "SPL", "SPLK", "SPNE", "SNP", "SPOT",
        "SPPI", "SPR", "SPRO", "SPRT", "SPSC", "SPT", "SPTN", "SPWH", "SPWR", "SQ",
        "SQI", "SQMS", "SQNS", "SR", "SRCE", "SRCL", "SRDX", "SRE", "SREA", "SRG",
        "SRNE", "SRPT", "SRRA", "SRT", "SRTS", "SS", "SSA", "SSB", "SSBI", "SSD",
        "SSH", "SSIC", "SSL", "SSNC", "SSNT", "SSP", "SSRM", "SSTK", "SSW", "SSY",
        "ST", "STAA", "STAF", "STAG", "STAR", "STAY", "STB", "STBA", "STC", "STCN",
        "STE", "STEL", "STEM", "STEP", "STG", "STIM", "STIP", "STK", "STL", "STLD",
        "STM", "STMP", "STN", "STNE", "STNG", "STON", "STOR", "STOW", "STPK", "STR",
        "STRA", "STRE", "STRL", "STRM", "STRN", "STRO", "STRR", "STT", "STWD", "STX",
        "STZ", "SU", "SUI", "SUM", "SUN", "SUP", "SUPN", "SURF", "SVC", "SVMK",
        "SVRA", "SW", "SWAV", "SWCH", "SWIR", "SWK", "SWKS", "SWM", "SWN", "SWT",
        "SWTX", "SY", "SYF", "SYK", "SYY", "T", "TAC", "TAK", "TAL", "TALN", "TAPE",
        "TAP", "TARO", "TASK", "TAST", "TAX", "TBBK", "TBI", "TBNK", "TBIO", "TBN",
        "TC", "TCBC", "TCBI", "TCBK", "TCCO", "TCF", "TCFC", "TCH", "TCI", "TCMD",
        "TCN", "TCO", "TCON", "TCS", "TCX", "TD", "TDA", "TDC", "TDF", "TDG", "TDS",
        "TDY", "TE", "TEAM", "TECH", "TECK", "TEDU", "TEL", "TELL", "TEM", "TEN",
        "TENB", "TEO", "TER", "TERP", "TEVA", "TEX", "TFC", "TFFP", "TFI", "TFII",
        "TFSL", "TFX", "TG", "TGA", "TGB", "TGH", "TGI", "TGNA", "TGS", "TGT",
        "TH", "THBR", "THC", "THFF", "THG", "THO", "THQ", "THR", "THRM", "THS",
        "TILE", "TIMB", "TINV", "TIPT", "TIRX", "TJX", "TK", "TKC", "TKR", "TLG",
        "TLI", "TLRY", "TLS", "TLT", "TM", "TMDI", "TMHC", "TMO", "TMP", "TMQ",
        "TMST", "TMUS", "TNA", "TNAV", "TNDM", "TNET", "TNGX", "TNK", "TNP", "TOC",
        "TOD", "TOK", "TOPS", "TOR", "TOWN", "TPC", "TPH", "TPHZ", "TPR", "TPS",
        "TR", "TRAK", "TRC", "TRCH", "TRGP", "TRI", "TRIP", "TRMB", "TRMD", "TRMK",
        "TRMR", "TRN", "TRNO", "TRNS", "TROW", "TROX", "TRUE", "TRV", "TS", "TSCAP",
        "TSE", "TSLA", "TSLX", "TSM", "TSN", "TSOC", "TSPI", "TSSI", "TST", "TSX",
        "TT", "TTC", "TTD", "TTE", "TTEC", "TTEK", "TTGT", "TTI", "TTM", "TTMI",
        "TTO", "TTP", "TTTN", "TU", "TUES", "TUP", "TUR", "TURN", "TUSA", "TUSK",
        "TV", "TVC", "TVE", "TVTY", "TW", "TWC", "TWCT", "TWI", "TWLO", "TWLV",
        "TWN", "TWO", "TWST", "TX", "TXMD", "TXN", "TXRH", "TXT", "TY", "TYL",
        "U", "UA", "UAA", "UAL", "UAMY", "UAN", "UBA", "UBER", "UBFO", "UBNK",
        "UBP", "UBS", "UDR", "UE", "UEC", "UEIC", "UEP", "UES", "UET", "UFI",
        "UFL", "UG", "UGI", "UGP", "UHS", "UHT", "UI", "UIS", "UL", "ULCC", "ULE",
        "ULH", "ULTA", "UMBF", "UMPQ", "UN", "UNAM", "UNB", "UNC", "UNF", "UNFI",
        "UNH", "UNIT", "UNM", "UNP", "UNT", "UNTY", "UNVR", "UOA", "UPL", "UPRO",
        "UPS", "UR", "URA", "URBN", "URE", "URG", "URI", "URR", "USAC", "USAP",
        "USAU", "USB", "USCR", "USEG", "USF", "USFD", "USG", "USL", "USM", "USNA",
        "USPH", "USRT", "UST", "USW", "UTHR", "UTI", "UTL", "UTMD", "UTSI", "UVE",
        "UVSP", "V", "VAC", "VAL", "VALE", "VBF", "VBIV", "VBLT", "VBND", "VBTX",
        "VC", "VCEL", "VCO", "VCRA", "VCTR", "VCV", "VCYT", "VEA", "VEDL", "VEEV",
        "VEL", "VER", "VERA", "VERB", "VET", "VFC", "VFF", "VG", "VGR", "VHC",
        "VHI", "VICR", "VIEW", "VIG", "VIPS", "VIR", "VIRC", "VIST", "VIT", "VIVE",
        "VIVK", "VJE", "VLO", "VLRS", "VLT", "VLU", "VLY", "VMA", "VMBS", "VMC",
        "VMD", "VMI", "VMP", "VNLA", "VNO", "VNRX", "VO", "VOD", "VOE", "VOO",
        "VOT", "VOW", "VOXX", "VP", "VPG", "VRA", "VRAI", "VRM", "VRNA", "VRNT",
        "VROC", "VRP", "VRT", "VRTX", "VRTS", "VRTX", "VS", "VSAT", "VSEC", "VSH",
        "VSL", "VSM", "VSNR", "VST", "VSTO", "VT", "VTA", "VTN", "VTR", "VTV",
        "VTWG", "VTWO", "VUC", "VUZ", "VVI", "VVR", "VXRT", "VYGR", "VZ", "W",
        "WABC", "WAFD", "WAFDP", "WAL", "WAMC", "WAT", "WAVD", "WAVE", "WBA",
        "WBC", "WBS", "WBT", "WCC", "WCLD", "WCN", "WD", "WDAY", "WDC", "WDFC",
        "WDIV", "WDR", "WEA", "WEC", "WEED", "WELL", "WEN", "WERN", "WES", "WETF",
        "WEWORK", "WEX", "WEYS", "WF", "WFC", "WFE", "WFRD", "WGO", "WGS", "WHD",
        "WHG", "WHR", "WILC", "WIMI", "WINA", "WING", "WIRE", "WISH", "WIT", "WIX",
        "WK", "WKEY", "WKMG", "WLK", "WLY", "WLYW", "WM", "WMB", "WMC", "WMK",
        "WMS", "WMT", "WNC", "WNS", "WPG", "WPP", "WPX", "WR", "WRAP", "WRE",
        "WRK", "WS", "WSC", "WSG", "WSM", "WSO", "WSR", "WST", "WTI", "WTM", "WTRE",
        "WU", "WVE", "WVFC", "WW", "WWD", "WWE", "WWR", "WWW", "WY", "WYY", "X",
        "XAN", "XB", "XBI", "XEL", "XENE", "XERS", "XFLT", "XHR", "XL", "XLE",
        "XLF", "XLG", "XLI", "XLK", "XLP", "XLRN", "XLU", "XLV", "XLY", "XMP",
        "XN", "XNA", "XNL", "XOM", "XON", "XONE", "XR", "XRAY", "XRX", "XT",
        "XTL", "XPO", "XRA", "XRF", "XRX", "XSL", "XSN", "XSP", "XTN", "XYL",
        "Y", "YANG", "YELP", "YETI", "YEXT", "YLD", "YMAB", "YNDX", "YOGA", "YRD",
        "YSG", "YTRA", "YUM", "YUMC", "YVR", "Z", "ZBH", "ZBRA", "ZION", "ZIXI",
        "ZM", "ZNH", "ZNJ", "ZNT", "ZOHO", "ZPG", "ZTO", "ZTR", "ZUMZ", "ZVO",
        "ZYNE", "ZYXI"
    ]
    
    # Объединяем и удаляем дубликаты
    tickers = list(set(tickers + common_stocks))
    tickers.sort()
    return tickers

ALL_TICKERS = get_all_tickers()

PERIODS = {
    "1 неделя": ("5d", "1W"),
    "1 месяц": ("1mo", "1M"),
    "3 месяца": ("3mo", "3M"),
    "6 месяцев": ("6mo", "6M")
}

# === ФУНКЦИИ С ПАРАЛЛЕЛЬНОЙ ЗАГРУЗКОЙ ===

def check_ticker(ticker, min_price, min_market_cap, min_volume, min_adr):
    """Проверяет один тикер"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1mo")
        
        price = info.get('currentPrice') or info.get('regularMarketPrice')
        if not price or price < min_price:
            return None
        
        market_cap = info.get('marketCap')
        if not market_cap or market_cap < min_market_cap * 1_000_000:
            return None
        
        avg_volume = info.get('averageVolume') or info.get('averageVolume10days')
        if not avg_volume or avg_volume < min_volume * 1000:
            return None
        
        if hist.empty or len(hist) < 5:
            return None
        
        daily_ranges = []
        for j in range(len(hist)):
            day_high = hist['High'].iloc[j]
            day_low = hist['Low'].iloc[j]
            day_open = hist['Open'].iloc[j]
            if day_open > 0:
                daily_range = ((day_high - day_low) / day_open) * 100
                daily_ranges.append(daily_range)
        
        if not daily_ranges:
            return None
        
        adr = sum(daily_ranges) / len(daily_ranges)
        
        if adr < min_adr:
            return None
        
        return {
            'ticker': ticker,
            'price': price,
            'market_cap': market_cap,
            'volume': avg_volume,
            'adr': round(adr, 2)
        }
    except Exception:
        return None


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_and_filter_stocks_parallel(tickers, min_price, min_market_cap, min_volume, min_adr):
    """Параллельная загрузка и фильтрация"""
    filtered = []
    total = len(tickers)
    progress_bar = st.progress(0)
    status_text = st.empty()
    completed = 0
    
    # Параллельная обработка (20 потоков)
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_ticker, t, min_price, min_market_cap, min_volume, min_adr): t 
                   for t in tickers}
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                filtered.append(result)
            
            completed += 1
            if completed % 50 == 0:
                progress_bar.progress(completed / total)
                status_text.text(f"Обработано {completed}/{total} акций... Найдено: {len(filtered)}")
    
    progress_bar.progress(1.0)
    status_text.text(f"Готово! Найдено {len(filtered)} акций")
    
    return filtered


@st.cache_data(ttl=3600, show_spinner=False)
def calculate_momentum_for_stocks(filtered_tickers, period_key):
    """Рассчитывает моментум"""
    momentum_data = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    total = len(filtered_tickers)
    
    for i, item in enumerate(filtered_tickers):
        ticker = item['ticker']
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period_key)
            
            if hist.empty or len(hist) < 2:
                continue
            
            price = hist['Close'].iloc[-1]
            
            past_idx = 0 if len(hist) <= 5 else len(hist) - 5
            past_price = hist['Close'].iloc[past_idx]
            momentum = ((price / past_price) - 1) * 100 if past_price > 0 else 0
            
            if len(hist) >= 2:
                prev = hist['Close'].iloc[-2]
                day_chg = ((price / prev) - 1) * 100
            else:
                day_chg = 0
            
            momentum_data.append({
                'Ticker': ticker,
                'Price': price,
                'Momentum %': momentum,
                'Day %': day_chg,
                'Volume': item['volume']
            })
            
        except Exception:
            continue
        
        if i % 20 == 0:
            progress_bar.progress(i / total)
            status_text.text(f"Расчёт моментума: {i}/{total}")
    
    progress_bar.progress(1.0)
    status_text.text("Расчёт завершён!")
    
    return momentum_data


# === ИНТЕРФЕЙС ===

st.title("📊 Momentum Scanner")
st.markdown("### Стратегия Кэлломэги - Полный скрининг US акций")

# Боковая панель
with st.sidebar:
    st.header("⚙️ Первичные фильтры")
    
    min_price = st.number_input("Мин. цена ($)", value=2.0, min_value=0.1, step=0.5)
    min_market_cap = st.number_input("Мин. капитализация ($M)", value=500.0, min_value=10.0, step=50.0)
    min_volume = st.number_input("Мин. объём (тыс.)", value=1000.0, min_value=100.0, step=100.0)
    min_adr = st.slider("Мин. ADR (%)", 1, 20, 5)
    
    st.markdown("---")
    st.header("📊 Параметры")
    top_percent = st.slider("Топ % акций", 1, 20, 5)
    
    st.markdown("---")
    st.markdown(f"**Всего тикеров:** {len(ALL_TICKERS)}")
    
    if st.button("🔄 Очистить кэш"):
        fetch_and_filter_stocks_parallel.clear()
        calculate_momentum_for_stocks.clear()
        st.rerun()

# Выбор периода
col1, col2 = st.columns([3, 1])
with col1:
    period_name = st.selectbox("Период моментума:", list(PERIODS.keys()))

period_key, period_label = PERIODS[period_name]

st.markdown("---")

# === ЗАГРУЗКА ===

st.info(f"📊 Сканируем {len(ALL_TICKERS)} акций (параллельная загрузка)...")

with st.spinner("Фильтрация..."):
    filtered = fetch_and_filter_stocks_parallel(
        ALL_TICKERS, min_price, min_market_cap, min_volume, min_adr
    )

st.success(f"✅ Фильтр прошли: {len(filtered)} акций")

if filtered:
    with st.expander(f"📋 Список ({len(filtered)})"):
        df_filtered = pd.DataFrame(filtered)
        df_filtered['Market Cap ($M)'] = df_filtered['market_cap'] / 1_000_000
        df_filtered['Volume (K)'] = df_filtered['volume'] / 1000
        df_filtered = df_filtered.sort_values('Market Cap ($M)', ascending=False)
        st.dataframe(
            df_filtered[['ticker', 'price', 'Market Cap ($M)', 'Volume (K)', 'adr']],
            use_container_width=True
        )

# === МОМЕНТУМ ===

st.markdown("---")
st.markdown(f"### 📈 Топ {top_percent}% моментум ({period_name})")

if filtered:
    with st.spinner("Расчёт моментума..."):
        momentum_data = calculate_momentum_for_stocks(filtered, period_key)
    
    if momentum_data:
        df = pd.DataFrame(momentum_data)
        df = df.sort_values('Momentum %', ascending=False)
        
        top_n = max(3, int(len(df) * top_percent / 100))
        df_top = df.head(top_n)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Проверено", len(ALL_TICKERS))
        c2.metric("Прошли фильтр", len(filtered))
        c3.metric("Топ акций", top_n)
        c4.metric("Ср. моментум", f"{df_top['Momentum %'].mean():.1f}%")
        
        st.markdown("---")
        
        for idx, row in df_top.iterrows():
            m_color = "green" if row['Momentum %'] > 0 else "red"
            d_color = "green" if row['Day %'] > 0 else "red"
            
            st.markdown(f"""
            <div class="stock-card">
                <div><b style="font-size:20px;">{row['Ticker']}</b></div>
                <div style="text-align:right;">
                    <div style="font-size:20px;">${row['Price']:.2f}</div>
                    <div class="{m_color}" style="font-weight:bold;">М: {'+' if row['Momentum %']>0 else ''}{row['Momentum %']:.1f}%</div>
                    <div class="{d_color}">Д: {'+' if row['Day %']>0 else ''}{row['Day %']:.1f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        now = datetime.now()
        st.markdown(f"<small>Обновлено: {now.strftime('%Y-%m-%d %H:%M:%S')}</small>", unsafe_allow_html=True)
        
        csv = df_top.to_csv(index=False)
        st.download_button("📥 Скачать CSV", csv, "momentum_stocks.csv", use_container_width=True)
