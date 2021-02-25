from bokeh.plotting import figure, output_file, output_notebook
from bokeh.models.widgets import Select,Button
from bokeh.io import curdoc
from bokeh.palettes import brewer
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, FactorRange,  CustomJS, Title, PreText, DataTable, TableColumn, Patches, Plot, LabelSet
from bokeh.transform import dodge
from datetime import datetime
import pandas as pd
import numpy as np
import math

# Connect MySQL
import mysql.connector


maxdb = mysql.connector.connect(
  host = "35.185.158.227",
  port = "8101",
  user = "sias_ntus",
  password = "sias_ntus20191101",
  database = "sias_ntus",
  )
cursor=maxdb.cursor()

data = {}

def get_nameArray():
    cursor.execute("SELECT u_id,name,line_id FROM users")
    s1 = cursor.fetchall()
    df = pd.DataFrame(data=s1)
    df2 = df[df[0]>1]
    unique = []
    nameArray = df2[1].values.tolist()
    for name in nameArray:
        if name not in unique:
            unique.append(name)
    return unique

def get_IDArray(name):
    command = ("SELECT line_id FROM users Where name = %s")
    temp = []
    temp.append(name)
    cursor.execute(command,tuple(temp))
    line_id = cursor.fetchall()
    callbackIDArray = []
    for i in range(len(line_id)):
        callbackIDArray.append(line_id[i][0])
    return callbackIDArray

def get_u_id(name,lineID):
    command = "SELECT u_id,line_id FROM users Where name = %s"
    temp = []
    temp.append(name)
    cursor.execute(command,tuple(temp))
    array = cursor.fetchall()
    
    for i in range(len(array)):
        if array[i][1] == lineID:
            u_id = array[i][0]
            return u_id

def get_ubi_id(u_id):
    temp = []
    command = "SELECT ubi_id FROM users_body_info Where u_id = %s"
    temp.append(str(u_id))
    cursor.execute(command,tuple(temp))
    array = cursor.fetchall()
    ubi_id = []
    for i in range(len(array)):
        ubi_id.append(str(array[i][0]))
    
    return ubi_id

def get_fm_id(ubi_id):
    temp = []
    command = "SELECT fm_id FROM functional_measurement Where ubi_id = %s"
    temp.append(str(ubi_id))
    cursor.execute(command,tuple(temp))
    fm_id = cursor.fetchall()
    if not fm_id:
        return -1
    return fm_id



def timestamp2datetime(timestamp, convert_to_local=False):
    ''' Converts UNIX timestamp to a datetime object. '''
    if isinstance(timestamp, (int)):
        dt = datetime.fromtimestamp(timestamp)
        return dt

def getdata(ubi_id):
    command = "SELECT * FROM muscles_joints_measurement Where ubi_id = %s"
    ubi = []
    ubi.append(str(ubi_id))
    cursor.execute(command,tuple(ubi))
    result = cursor.fetchall()

    if not result:
        data['date'] = timestamp2datetime(631123200,True)
        for i in data.keys():
            if i == 'date':
                continue
            else:
                data[i] = '0.00'
        return data
    df = pd.DataFrame(data=result)
    df.dropna()
    tag = math.floor(int(df[3][0])/1000)
    dt = timestamp2datetime(tag,True)
    data['date'] = dt
    
    data['lx_lf_rom_r'] = '%.2f' % df[4][0]
    data['lx_lf_rom_l'] = '%.2f' % df[5][0]
    if data['lx_lf_rom_r'] and data['lx_lf_rom_l'] == '0.00':
        data['lumbarDf'] = '0.00'
    else:
        data['lumbarDf'] = '%.2f' % (((abs(df[4][0]-df[5][0]))/(df[4][0]+df[5][0]))*100)
    data['tx_r_rom_r'] = '%.2f' % df[6][0]
    data['tx_r_rom_l'] = '%.2f' % df[7][0]
    if data['tx_r_rom_r'] and data['tx_r_rom_l'] == '0.00':
        data['tx_Df'] = '0.00'
    else:
        data['tx_Df'] = '%.2f' % (((abs(df[6][0] - df[7][0]))/(df[6][0] + df[7][0]))*100)
    
    data['gh_er_rom_r'] = '%.2f' % df[8][0]
    data['gh_er_rom_l'] = '%.2f' % df[9][0]
    data['gh_ir_rom_r'] = '%.2f' % df[10][0]
    data['gh_ir_rom_l'] = '%.2f' % df[11][0]
    data['GIRD'] = '%.2f' % abs(df[10][0]-df[11][0])
    data['GERD'] = '%.2f' % abs(df[8][0]-df[9][0])
    if data['GERD'] == '0.00':
        data['GIRD_df'] = '0.00'
    else:
        data['GIRD_df'] = int(float(data['GIRD'])/float(data['GERD'])*100)
    data['gh_er_mmt_r'] = '%.2f' % df[12][0]
    data['gh_er_mmt_l'] = '%.2f' % df[13][0]
    if data['gh_er_mmt_r'] and data['gh_er_mmt_l'] == '0.00':
        data['gh_er_mmt_df'] = '0.00'
    else:
        data['gh_er_mmt_df'] = '%.2f' % (((abs(df[12][0] - df[13][0]))/(df[12][0] + df[13][0]))*100)
    data['gh_ir_mmt_r'] = '%.2f' % df[14][0]
    data['gh_ir_mmt_l'] = '%.2f' % df[15][0]
    if data['gh_ir_rom_r'] and data['gh_ir_rom_l'] == '0.00':
        data['gh_ir_mmt_df'] = '0.00'
    else:
        data['gh_ir_mmt_df'] = '%.2f' % (((abs(df[14][0] - df[15][0]))/(df[14][0] + df[15][0]))*100)
    if df[16][0] is None:
        data['e_f_mmt_r'] = '0.00'
    else:
        data['e_f_mmt_r'] = '%.2f' % df[16][0]
    if df[17][0] is None:
        data['e_f_mmt_l'] = '0.00'
    else:
        data['e_f_mmt_l'] = '%.2f' % df[17][0]
    if data['e_f_mmt_r'] and data['e_f_mmt_l'] == '0.00':
        data['e_f_mmt_df'] = '0.00'
    else:
        data['e_f_mmt_df'] = '%.2f' % (((abs(df[16][0] - df[17][0]))/(df[16][0] + df[17][0]))*100)
    if df[18][0] is None:
        data['e_e_mmt_r'] = '0.00'
    else:
        data['e_e_mmt_r'] = '%.2f' % df[18][0]
    if df[19][0] is None:
        data['e_e_mmt_l'] = '0.00'
    else:
        data['e_e_mmt_l'] = '%.2f' % df[19][0]
    if data['e_e_mmt_r'] and data['e_e_mmt_l'] == '0.00':
        data['e_e_mmt_df'] = '0.00'
    else:
        data['e_e_mmt_df'] = '%.2f' % (((abs(df[18][0] - df[19][0]))/(df[18][0] + df[19][0]))*100)
    data['ank_inver_mmt_r'] = '%.2f' % df[20][0]
    data['ank_inver_mmt_l'] = '%.2f' % df[21][0]
    data['ank_ever_mmt_r'] = '%.2f' % df[22][0]
    data['ank_ever_mmt_l'] = '%.2f' % df[23][0]
    if data['ank_inver_mmt_r'] and data['ank_inver_mmt_l'] == '0.00':
        data['ank_inver_mmt_df'] = '0.00'
    else:
        data['ank_inver_mmt_df'] = '%.2f' % (((abs(df[20][0] - df[21][0]))/(df[20][0] + df[21][0]))*100)
    if data['ank_ever_mmt_r'] and data['ank_ever_mmt_l'] == '0.00':
        data['ank_ever_mmt_df'] = '0.00'
    else:
        data['ank_ever_mmt_df'] = '%.2f' % (((abs(df[22][0] - df[23][0]))/(df[22][0] + df[23][0]))*100)
    data['gh_horiadd_mmt_r'] = '%.2f' % df[24][0]
    data['gh_horiadd_mmt_l'] = '%.2f' % df[25][0]
    if data['gh_horiadd_mmt_r'] and data['gh_horiadd_mmt_l'] == '0.00':
        data['gh_horiadd_mmt_df'] = '0.00'
    else:
        data['gh_horiadd_mmt_df'] = '%.2f' % (((abs(df[24][0] - df[25][0]))/(df[24][0] + df[25][0]))*100)
    data['gh_horiabd_mmt_r'] = '%.2f' % df[26][0]
    data['gh_horiabd_mmt_l'] = '%.2f' % df[27][0]
    if data['gh_horiabd_mmt_r'] and data['gh_horiabd_mmt_l'] == '0.00':
        data['gh_horiabd_mmt_df'] = '0.00'
    else:
        data['gh_horiabd_mmt_df'] = '%.2f' % (((abs(df[26][0] - df[27][0]))/(df[26][0] + df[27][0]))*100)
    data['myo_t_f_r'] = '%.2f' % df[28][0]
    data['myo_t_f_l'] = '%.2f' % df[29][0]
    if data['myo_t_f_r'] and data['myo_t_f_l'] == '0.00':
        data['myo_t_f_df'] = '0.00'
    else:
        data['myo_t_f_df'] = '%.2f' % (((abs(df[28][0] - df[29][0]))/(df[28][0] + df[29][0]))*100)
    data['myo_t_s_r'] = '%.2f' % df[30][0]
    data['myo_t_s_l'] = '%.2f' % df[31][0]
    if data['myo_t_s_r'] and data['myo_t_s_l'] == '0.00':
        data['myo_t_s_df'] = '0.00'
    else:
        data['myo_t_s_df'] = '%.2f' % (((abs(df[30][0] - df[31][0]))/(df[30][0] + df[31][0]))*100)
    data['myo_t_d_r'] = '%.2f' % df[32][0]
    data['myo_t_d_l'] = '%.2f' % df[33][0]
    if data['myo_t_d_r'] and data['myo_t_d_l'] == '0.00':
        data['myo_t_d_df'] = '0.00'
    else:
        data['myo_t_d_df'] = '%.2f' % (((abs(df[32][0] - df[33][0]))/(df[32][0] + df[33][0]))*100)
    data['myo_es_s_f_r'] = '%.2f' % df[40][0]
    data['myo_es_s_f_l'] = '%.2f' % df[41][0]
    if data['myo_es_s_f_r'] and data['myo_es_s_f_l'] == '0.00':
        data['myo_es_s_f_df'] = '0.00'
    else:
        data['myo_es_s_f_df'] = '%.2f' % (((abs(df[40][0] - df[41][0]))/(df[40][0] + df[41][0]))*100)
    data['myo_es_s_s_r'] = '%.2f' % df[44][0]
    data['myo_es_s_s_l'] = '%.2f' % df[45][0]
    if data['myo_es_s_s_r'] and data['myo_es_s_s_l'] == '0.00':
        data['myo_es_s_s_df'] = '0.00'
    else:
        data['myo_es_s_s_df'] = '%.2f' % (((abs(df[44][0] - df[45][0]))/(df[44][0] + df[45][0]))*100)
    data['myo_es_s_d_r'] = '%.2f' % df[48][0]
    data['myo_es_s_d_l'] = '%.2f' % df[49][0]
    if data['myo_es_s_d_r'] and data['myo_es_s_d_l'] == '0.00':
        data['myo_es_s_d_df'] = '0.00'
    else:
        data['myo_es_s_d_df'] = '%.2f' % (((abs(df[48][0] - df[49][0]))/(df[48][0] + df[49][0]))*100)

    command2 = "SELECT * FROM functional_measurement Where ubi_id = %s"
    cursor.execute(command2,tuple(ubi))
    result2 = cursor.fetchall()

    df2 = pd.DataFrame(data=result2)
    df2.dropna()
    
    data['squat'] = df2[8][0]
    data['hurdle'] = df2[15][0]
    data['lunge'] = df2[22][0]
    data['mobility'] = df2[29][0]
    data['slr'] = df2[36][0]
    data['pushup'] = df2[40][0]
    data['stability'] = df2[47][0]
    data['fms_total'] = df2[48][0]

    command3 = "SELECT * FROM users_investigation Where ubi_id = %s"
    cursor.execute(command3,tuple(ubi))
    result3 = cursor.fetchall()
    df3 = pd.DataFrame(data=result3)
    if not df3[31][0]:
        data['spf_balance_l_a'] = '0.00'
    else:
        data['spf_balance_l_a'] = '%.2f' % df3[31][0]
    if not df3[32][0]:
        data['spf_balance_l_pm'] = '0.00'
    else:
        data['spf_balance_l_pm'] = '%.2f' % df3[32][0]
    if not df3[33][0]:
        data['spf_balance_l_pl'] = '0.00'
    else:
        data['spf_balance_l_pl'] = '%.2f' % df3[33][0]
    if not df3[34][0]:
        data['spf_balance_r_a'] = '0.00'
    else:
        data['spf_balance_r_a'] = '%.2f' % df3[34][0]
    if not df3[35][0]:
        data['spf_balance_r_pm'] = '0.00'
    else:
        data['spf_balance_r_pm'] = '%.2f' % df3[35][0]
    if not df3[36][0]:
        data['spf_balance_r_pl'] = '0.00'
    else:
        data['spf_balance_r_pl'] = '%.2f' % df3[36][0]

    command4 = "SELECT * FROM users_body_info Where ubi_id = %s"
    cursor.execute(command4,tuple(ubi))
    result4 = cursor.fetchall()
 
    df4 = pd.DataFrame(data=result4)

    data['rl_len'] = '%.2f' % df4[20][0]
    data['ll_len'] = '%.2f' % df4[21][0]
    # print(data['spf_balance_r_a'])
    # print(type(data['spf_balance_r_a']))
    # print(type(float(data['spf_balance_r_a'])))
    if not data['rl_len'] or data['rl_len']=='0.00':
        data['right_scores'] = '0.00'
    else:
        data['right_scores'] = '%.2f' % ((float(data['spf_balance_r_a'])+float(data['spf_balance_r_pm'])+float(data['spf_balance_r_pl']))/(3*float(data['rl_len']))*100)
    if not data['ll_len'] or data['ll_len']=='0.00':
        data['left_scores'] = '0.00'
    else:
        data['left_scores'] = '%.2f' % ((float(data['spf_balance_l_a'])+float(data['spf_balance_l_pm'])+float(data['spf_balance_l_pl']))/(3*float(data['ll_len']))*100)
    return data

# print(get_nameArray()[0])
# print(get_IDArray('林子鈞'))
# print(get_u_id('林子鈞','A108100602'))
# print(get_ubi_id(get_u_id('林子鈞','A108100602')))
# print(get_ubi_id(get_u_id('林子鈞','A108100602'))[0])


select1 = Select(value = get_nameArray()[0], options = get_nameArray())
select2 = Select(value = get_IDArray(get_nameArray()[0])[1], options = get_IDArray(select1.value))
select3 = Select(value = get_ubi_id(get_u_id(select1.value,select2.value))[0], options = get_ubi_id(get_u_id(select1.value,select2.value)))

#-----Rador Plot---------#
num_vars = 7
centre = 3

theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)
# rotate theta such that the first axis is at the top
theta += np.pi/2

def unit_poly_verts(theta, centre ):
    """Return vertices of polygon for subplot axes.
    This polygon is circumscribed by a unit circle centered at (0.5, 0.5)
    """
    x0, y0, r = [centre ] * 3
    verts = [(r*np.cos(t) + x0, r*np.sin(t) + y0) for t in theta]
    return verts

def radar_patch(r, theta, centre ):
    """ Returns the x and y coordinates corresponding to the magnitudes of 
    each variable displayed in the radar plot
    """
    # offset from centre of circle
    r = r/3
    offset = 0
    yt = (r*centre + offset) * np.sin(theta) + centre 
    xt = (r*centre + offset) * np.cos(theta) + centre 
    return xt, yt

verts = unit_poly_verts(theta, centre)
x = [v[0] for v in verts] 
y = [v[1] for v in verts] 

#-------------------------------------------------------#

dataset = getdata(select3.value)
datestat = PreText(text='',width=500)
bodyROM = ['腰椎旋轉', '胸椎旋轉']
years = ['左邊', '右邊', '差值(%)']
x1 = [ (rom, year) for rom in bodyROM for year in years ]
time = datetime.strftime(dataset['date'],'%Y-%m-%d')
dataset['date'] = time
datestat.text = dataset['date']
counts = dataset['lx_lf_rom_r'], dataset['lx_lf_rom_l'], dataset['lumbarDf'], dataset['tx_r_rom_r'], dataset['tx_r_rom_l'], dataset['tx_Df'] # like an hstack
# 肌肉張力測量
# 坐姿斜方肌
group1 = ['肌肉張力(Hz)','肌肉硬度(N/m)','肌肉彈性']
group1_y = ['左邊','右邊','差值(%)']
group1_x = [ (a,b) for a in group1 for b in group1_y ]
counts16 = dataset['myo_t_f_l'], dataset['myo_t_f_r'], dataset['myo_t_f_df'], dataset['myo_t_s_l'], dataset['myo_t_s_r'], dataset['myo_t_s_df'], dataset['myo_t_d_l'], dataset['myo_t_d_r'], dataset['myo_t_d_df']
counts16_table1 = dict(
        item=['肌肉張力(Hz)','肌肉硬度(N/m)','肌肉彈性'],
        Left=[dataset['myo_t_f_l'], dataset['myo_t_s_l'], dataset['myo_t_d_l']],
        Right=[dataset['myo_t_f_r'], dataset['myo_t_s_r'], dataset['myo_t_d_r']],
        DF=[dataset['myo_t_f_df'], dataset['myo_t_s_df'], dataset['myo_t_d_df']]
    )
columns_table1 = [
        TableColumn(field="item", title="項目"),
        TableColumn(field="Left", title="左側"),
        TableColumn(field="Right", title="右側"),
        TableColumn(field="DF", title="差值(%)"),
    ]
#坐姿豎棘肌
group2 = ['肌肉張力(Hz)','肌肉硬度(N/m)','肌肉彈性']
group2_y = ['左邊','右邊','差值(%)']
group2_x = [ (a,b) for a in group2 for b in group2_y ]
counts17 = dataset['myo_es_s_f_l'], dataset['myo_es_s_f_r'], dataset['myo_es_s_f_df'], dataset['myo_es_s_s_l'], dataset['myo_es_s_s_r'], dataset['myo_es_s_s_df'], dataset['myo_es_s_d_l'], dataset['myo_es_s_d_r'], dataset['myo_es_s_d_df']
counts17_table1 = dict(
        item=['肌肉張力(Hz)','肌肉硬度(N/m)','肌肉彈性'],
        Left=[dataset['myo_es_s_f_l'], dataset['myo_es_s_s_l'], dataset['myo_es_s_d_l']],
        Right=[dataset['myo_es_s_f_r'], dataset['myo_es_s_s_r'], dataset['myo_es_s_d_r']],
        DF=[dataset['myo_es_s_f_df'], dataset['myo_es_s_s_df'], dataset['myo_es_s_d_df']]
    )
#-----------------------------#
# plot Shoulder

regions = ['內轉', '外轉']
factors = ["左肩","右肩"]
source2 = ColumnDataSource(data=dict(
    x = factors,
    內轉 = [dataset['gh_ir_rom_l'],dataset['gh_ir_rom_r']],
    外轉 = [dataset['gh_er_rom_l'],dataset['gh_er_rom_r']],
))

# plot GIRD.GERD
regions3 = ['GIRD','GERD','GIRD/GERD(%)']
counts3 = dataset['GIRD'], dataset['GERD'], dataset['GIRD_df']

#----MMT----#
# plot shoulder
# 外轉
regions4 = ['左肩','右肩','差值(%)']
counts4 = dataset['gh_er_mmt_l'],dataset['gh_er_mmt_r'],dataset['gh_er_mmt_df']
# 內轉
regions5 = ['左肩','右肩','差值(%)']
counts5 = dataset['gh_ir_mmt_l'],dataset['gh_ir_mmt_r'],dataset['gh_ir_mmt_df']
# plot elbow
# Elbow Flaxion
# regions6 = ['左肘','右肘','差值(%)']
# counts6 = dataset['e_f_mmt_l'],dataset['e_f_mmt_r'],dataset['e_f_mmt_df']
#Elbow Extension
regions7 = ['左肘','右肘','差值(%)']
counts7 = dataset['e_e_mmt_l'],dataset['e_e_mmt_r'],dataset['e_e_mmt_df']
#Ankle inversion
regions8 = ['左踝','右踝','差值(%)']
counts8 = dataset['ank_inver_mmt_l'],dataset['ank_inver_mmt_r'],dataset['ank_inver_mmt_df']
#Ankle eversion
regions9 = ['左踝','右踝','差值(%)']
counts9 = dataset['ank_ever_mmt_l'],dataset['ank_ever_mmt_r'],dataset['ank_ever_mmt_df']
#shoulder horizontal adduction
regions10 = ['左肩','右肩','差值(%)']
counts10 = dataset['gh_horiadd_mmt_l'],dataset['gh_horiadd_mmt_r'],dataset['gh_horiadd_mmt_df']
#shoulder horizontal abduction
regions11 = ['左肩','右肩','差值(%)']
counts11 = dataset['gh_horiabd_mmt_l'],dataset['gh_horiabd_mmt_r'],dataset['gh_horiabd_mmt_df']
f1 = np.array([int(float(dataset['squat'])), int(float(dataset['hurdle'])), int(float(dataset['lunge'])), int(float(dataset['mobility'])), int(float(dataset['slr'])), int(float(dataset['pushup'])), int(float(dataset['stability']))])
flist = f1   
xt, yt = radar_patch(flist, theta, 3)
counts18 = dict(xt = xt,
                yt = yt
)
# Y 平衡
regions19 = ['左腳','右腳']
direction = ['前','後內','後外','分數']

data19 = {'direction' : direction,
        '左腳':[dataset['spf_balance_l_a'],dataset['spf_balance_l_pm'],dataset['spf_balance_l_pl'],data['left_scores']],
        '右腳':[dataset['spf_balance_r_a'],dataset['spf_balance_r_pm'],dataset['spf_balance_r_pl'],data['right_scores']]}

source = ColumnDataSource(data=dict(x=x1, counts=counts))

source3 = ColumnDataSource(data=dict(regions3 = regions3, counts3 = counts3,color = brewer['Set1'][3]))
source4 = ColumnDataSource(data=dict(regions4 = regions4, counts4 = counts4,color = brewer['Set1'][3]))
source5 = ColumnDataSource(data=dict(regions5 = regions5, counts5 = counts5,color = brewer['Set1'][3]))
# source6 = ColumnDataSource(data=dict(regions6 = regions6, counts6 = counts6))
source7 = ColumnDataSource(data=dict(regions7 = regions7, counts7 = counts7,color = brewer['Set1'][3]))
source8 = ColumnDataSource(data=dict(regions8 = regions8, counts8 = counts8,color = brewer['Set1'][3]))
source9 = ColumnDataSource(data=dict(regions9 = regions9, counts9 = counts9,color = brewer['Set1'][3]))
source10 = ColumnDataSource(data=dict(regions10 = regions10, counts10 = counts10,color = brewer['Set1'][3]))
source11 = ColumnDataSource(data=dict(regions11 = regions11, counts11 = counts11,color = brewer['Set1'][3]))
source16 = ColumnDataSource(data=dict(group1_x = group1_x, counts16 = counts16))
source17 = ColumnDataSource(data=dict(group2_x = group2_x, counts17 = counts17))
source16_table1 = ColumnDataSource(data = counts16_table1)
source17_table1 = ColumnDataSource(data = counts17_table1)
text = ['深蹲','跨欄','直線前蹲','肩部活動','主動直膝抬腿','軀幹穩定伏地挺身','旋轉穩定性','']
source18 = ColumnDataSource(data = {'x':x + [3.0],'y':y + [6.0],'text':text})
source18_data = ColumnDataSource(data = counts18)
source19 = ColumnDataSource(data=data19)

def create_figure():

    p = figure(x_range=FactorRange(*x1), plot_height=250,
            toolbar_location=None, tools="")

    p.vbar(x = 'x', top='counts', width=0.4,source=source)
    p.title.text = ("軀幹與上下肢關節活動度")
    p.title.text_color = "black"
    p.title.text_font_size = "22px"
    p.add_layout(Title(text="腰椎 & 胸椎旋轉"), 'above')
    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xaxis.major_label_orientation = 1
    p.xgrid.grid_line_color = None

    p2 = figure(x_range=FactorRange(*factors), plot_height=250,
           toolbar_location=None, tools="",title = "肩關節活動度")

    p2.vbar_stack(regions, x='x', width=0.2, alpha=0.5, color=["blue", "red"], source=source2,legend_label=regions)

    p2.y_range.start = 0
    p2.y_range.end = 180
    p2.x_range.range_padding = 0.1
    p2.xaxis.major_label_orientation = 1
    p2.xgrid.grid_line_color = None
    p2.legend.location = "top_center"
    p2.legend.orientation = "vertical"

    p3 = figure(x_range=regions3, plot_height=250, title="GIRD & GERD",
             toolbar_location=None, tools="")

    p3.vbar(x='regions3', top='counts3', width=0.2, source=source3, color = 'color') #, legend_field="regions3"

    p3.xgrid.grid_line_color = None
    # p3.legend.orientation = "horizontal"
    # p3.legend.location = "top_center"

    p4 = figure(x_range=regions4, plot_height=250,toolbar_location=None, tools="")
    p4.vbar(x='regions4', top='counts4', width=0.2, source=source4, color = 'color')
    p4.title.text = ("肌力測量")
    p4.title.text_color = "black"
    p4.title.text_font_size = "22px"
    p4.add_layout(Title(text="肩外轉肌力"), 'above')
    p4.yaxis.axis_label = "lbs"

    p5 = figure(x_range=regions5, plot_height=250,toolbar_location=None, tools="",title = "肩內轉肌力")
    p5.vbar(x='regions5', top='counts5', width = 0.2, source = source5,color = 'color')
    p5.yaxis.axis_label = "lbs"

    # p6 = figure(x_range=regions6, plot_height=250,toolbar_location=None, tools="",title = "肘彎曲肌力")
    # p6.vbar(x='regions6', top='counts6', width = 0.2, source = source6)

    p7 = figure(x_range=regions7, plot_height=250,toolbar_location=None, tools="",title = "肘伸直肌力")
    p7.vbar(x='regions7', top='counts7', width = 0.2, source = source7, color = 'color')
    p7.yaxis.axis_label = "lbs"

    p8 = figure(x_range=regions8, plot_height=250,toolbar_location=None, tools="",title = "踝內旋肌力")
    p8.vbar(x='regions8', top='counts8', width = 0.2, source = source8, color = 'color')
    p8.yaxis.axis_label = "lbs"

    p9 = figure(x_range=regions9, plot_height=250,toolbar_location=None, tools="",title = "踝外旋肌力")
    p9.vbar(x='regions9', top='counts9', width = 0.2, source = source9, color = 'color')
    p9.yaxis.axis_label = "lbs"

    p10 = figure(x_range=regions10, plot_height=250,toolbar_location=None, tools="",title = "肩水平內收")
    p10.vbar(x='regions10', top='counts10', width = 0.2, source = source10, color = 'color')
    p10.yaxis.axis_label = "lbs"

    p11 = figure(x_range=regions11, plot_height=250,toolbar_location=None, tools="",title = "肩水平外展")
    p11.vbar(x='regions11', top='counts11', width = 0.2, source = source11, color = 'color')
    p11.yaxis.axis_label = "lbs"

    p16 = figure(x_range=FactorRange(*group1_x), plot_height=250,
            toolbar_location=None, tools="")

    p16.vbar(x = 'group1_x', top='counts16', width=0.4,source=source16)
    p16.title.text = ("肌肉張力測量")
    p16.title.text_color = "black"
    p16.title.text_font_size = "22px"
    p16.add_layout(Title(text="坐姿斜方肌"), 'above')
    p16.y_range.start = 0
    p16.x_range.range_padding = 0.1
    p16.xaxis.major_label_orientation = 1
    p16.xgrid.grid_line_color = None

    p17= figure(x_range=FactorRange(*group2_x), plot_height=250,title="坐姿豎棘肌",
            toolbar_location=None, tools="")

    p17.vbar(x = 'group2_x', top='counts17', width=0.4,source=source17)
    p17.y_range.start = 0
    p17.x_range.range_padding = 0.1
    p17.xaxis.major_label_orientation = 1
    p17.xgrid.grid_line_color = None

    p18 = figure(title="FMS - 雷達圖")
    p18.circle(x=[3,3], y=[3,3], radius=[1,2], fill_color=None, line_color="gray")
    p18.segment(x0=[3, 3, 3, 3, 3, 3, 3], y0=[3, 3, 3, 3, 3, 3, 3], x1=[x[0], x[1], x[2], x[3], x[4], x[5], x[6]],
            y1=[y[0], y[1], y[2], y[3], y[4], y[5], y[6]], color="gray", line_width=1)

    p18.line(x="x", y="y", source=source18)
    labels = LabelSet(x="x",y="y",text="text",source=source18)

    colors = ['red']    
    
    p18.patch(x='xt', y='yt', fill_alpha=0.15, fill_color=colors[0],source = source18_data)
    p18.add_layout(labels)

    # Y 平衡
    p19 = figure(x_range=direction, y_range=(0, 120), plot_height=250, title="Y 平衡撿測",
           toolbar_location=None, tools="")

    p19.vbar(x=dodge('direction', -0.12, range=p19.x_range), top='左腳', width=0.2, source=source19,
        color="#c9d9d3", legend_label="左腳")

    p19.vbar(x=dodge('direction',  0.12,  range=p19.x_range), top='右腳', width=0.2, source=source19,
        color="#718dbf", legend_label="右腳")

    p19.x_range.range_padding = 0.1
    p19.xgrid.grid_line_color = None
    p19.legend.location = "top_left"
    p19.legend.orientation = "horizontal"

    data_table = DataTable(source=source16_table1, columns=columns_table1, width=400, height=280)
    data_table2 = DataTable(source=source17_table1, columns=columns_table1, width=400, height=280)

    return column(row(p,p2,p3),row(p4,p5,p7),row(p8,p9,p10),p11,row(column(p16,data_table),column(p17,data_table2)),p18,p19)


def select1_change(attrname, old, new):
    select2.options = get_IDArray(new)
    select2.value = get_IDArray(new)[0]
    update()
def select2_change(attrname, old, new):
    select3.options = get_ubi_id(get_u_id(select1.value,new))
    select3.value = get_ubi_id(get_u_id(select1.value,new))[0]
    update()
def select3_change(attrname, old, new):
    update()

select1.on_change('value', select1_change)
select2.on_change('value', select2_change)
select3.on_change('value', select3_change)

def update():
    dataset = getdata(select3.value)
    x1 = [ (rom, year) for rom in bodyROM for year in years ]
    time = datetime.strftime(dataset['date'],'%Y-%m-%d')
    dataset['date']=time
    counts = dataset['lx_lf_rom_r'], dataset['lx_lf_rom_l'], dataset['lumbarDf'], dataset['tx_r_rom_r'], dataset['tx_r_rom_l'], dataset['tx_Df'] # like an hstack
    counts3 = dataset['GIRD'],dataset['GERD'], dataset['GIRD_df']
    counts4 = dataset['gh_er_mmt_l'],dataset['gh_er_mmt_r'],dataset['gh_er_mmt_df']
    counts5 = dataset['gh_ir_mmt_l'],dataset['gh_ir_mmt_r'],dataset['gh_ir_mmt_df']
    # counts6 = dataset['e_f_mmt_l'],dataset['e_f_mmt_r'],dataset['e_f_mmt_df']
    counts7 = dataset['e_e_mmt_l'],dataset['e_e_mmt_r'],dataset['e_e_mmt_df']
    counts8 = dataset['ank_inver_mmt_l'],dataset['ank_inver_mmt_r'],dataset['ank_inver_mmt_df']
    counts9 = dataset['ank_ever_mmt_l'],dataset['ank_ever_mmt_r'],dataset['ank_ever_mmt_df']
    counts10 = dataset['gh_horiadd_mmt_l'],dataset['gh_horiadd_mmt_r'],dataset['gh_horiadd_mmt_df']
    counts11 = dataset['gh_horiabd_mmt_l'],dataset['gh_horiabd_mmt_r'],dataset['gh_horiabd_mmt_df']
    counts16 = dataset['myo_t_f_l'], dataset['myo_t_f_r'], dataset['myo_t_f_df'], dataset['myo_t_s_l'], dataset['myo_t_s_r'], dataset['myo_t_s_df'], dataset['myo_t_d_l'], dataset['myo_t_d_r'], dataset['myo_t_d_df']
    counts16_table1 = dict(
        item=['肌肉張力(Hz)','肌肉硬度(N/m)','肌肉彈性'],
        Left=[dataset['myo_t_f_l'], dataset['myo_t_s_l'], dataset['myo_t_d_l']],
        Right=[dataset['myo_t_f_r'], dataset['myo_t_s_r'], dataset['myo_t_d_r']],
        DF=[dataset['myo_t_f_df'], dataset['myo_t_s_df'], dataset['myo_t_d_df']]
    )
    counts17 = dataset['myo_es_s_f_l'], dataset['myo_es_s_f_r'], dataset['myo_es_s_f_df'], dataset['myo_es_s_s_l'], dataset['myo_es_s_s_r'], dataset['myo_es_s_s_df'], dataset['myo_es_s_d_l'], dataset['myo_es_s_d_r'], dataset['myo_es_s_d_df']
    counts17_table1 = dict(
        item=['肌肉張力(Hz)','肌肉硬度(N/m)','肌肉彈性'],
        Left=[dataset['myo_es_s_f_l'], dataset['myo_es_s_s_l'], dataset['myo_es_s_d_l']],
        Right=[dataset['myo_es_s_f_r'], dataset['myo_es_s_s_r'], dataset['myo_es_s_d_r']],
        DF=[dataset['myo_es_s_f_df'], dataset['myo_es_s_s_df'], dataset['myo_es_s_d_df']]
    )
    f1 = np.array([int(float(dataset['squat'])), int(float(dataset['hurdle'])), int(float(dataset['lunge'])), int(float(dataset['mobility'])), int(float(dataset['slr'])), int(float(dataset['pushup'])), int(float(dataset['stability']))])
    flist = f1   
    xt, yt = radar_patch(flist, theta, 3)
    counts18 = dict(xt = xt,
                    yt = yt
    )
    data19 = {'direction' : direction,
        '左腳':[dataset['spf_balance_l_a'],dataset['spf_balance_l_pm'],dataset['spf_balance_l_pl'],data['left_scores']],
        '右腳':[dataset['spf_balance_r_a'],dataset['spf_balance_r_pm'],dataset['spf_balance_r_pl'],data['right_scores']]}
    datestat.text = dataset['date']
    print(dataset)
    source.data = dict(x=x1,counts=counts)
    source2.data = dict(
        x = factors,
        內轉 = [dataset['gh_ir_rom_l'],dataset['gh_ir_rom_r']],
        外轉 = [dataset['gh_er_rom_l'],dataset['gh_er_rom_r']],
        )
    source3.data = dict(regions3 = regions3, counts3 = counts3,color = brewer['Set1'][3])
    source4.data = dict(regions4 = regions4, counts4 = counts4,color = brewer['Set1'][3])
    source5.data = dict(regions5 = regions5, counts5 = counts5,color = brewer['Set1'][3])
    # source6.data = dict(region6 = regions6, counts6 = counts6)
    source7.data = dict(regions7 = regions7, counts7 = counts7,color = brewer['Set1'][3])
    source8.data = dict(regions8 = regions8, counts8 = counts8,color = brewer['Set1'][3])
    source9.data = dict(regions9 = regions9, counts9 = counts9,color = brewer['Set1'][3])
    source10.data = dict(regions10 = regions10, counts10 = counts10,color = brewer['Set1'][3])
    source11.data = dict(regions11 = regions11, counts11 = counts11,color = brewer['Set1'][3])
    source16.data = dict(group1_x = group1_x, counts16 = counts16)
    source16_table1.data = counts16_table1
    source17.data = dict(group2_x = group2_x, counts17 = counts17)
    source17_table1.data = counts17_table1
    source18.data = {'x':x + [3.0],'y':y + [6.0],'text':text}
    source18_data.data = counts18
    source19.data = data19
    create_figure()


layout = column(row(select1,select2,select3,datestat),create_figure())

curdoc().add_root(layout)