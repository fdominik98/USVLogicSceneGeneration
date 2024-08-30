from visualization.colreg_plot import ColregPlot
from visualization.data_parser import DataParser
from model.usv_env_desc_list import USV_ENV_DESC_LIST
from model.usv_environment import USVEnvironment

while(True):
    dp = DataParser()
    df, _ = dp.load_files()
    
    if df.size == 0:
        exit(0)

    config = USV_ENV_DESC_LIST[df['config_name'][0]]
    env = USVEnvironment(config).update(df['best_solution'][0])
    ColregPlot(env)
        
        