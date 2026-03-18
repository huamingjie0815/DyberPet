import re
import json
import glob
import time
import os.path
from datetime import datetime, timedelta
from sys import platform
from DyberPet.utils import text_wrap, get_child_folder

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap

from .utils import get_file_time, find_dir_with_subdir, convert_fv_versions

if platform == 'win32':
    basedir = ''
else:
    #from pathlib import Path
    basedir = os.path.dirname(__file__) #Path(os.path.dirname(__file__))
    #basedir = basedir.parent
    basedir = basedir.replace('\\','/')
    basedir = '/'.join(basedir.split('/')[:-1])


if platform == 'linux':
    configdir = os.path.dirname(os.environ['HOME']+'/.config/DyberPet/DyberPet')
else:
    configdir = basedir

num_hp_states = 4
# Copied from settings.py
LVL_BAR_V1 = [20, 120, 300, 600, 1200, 1800, 2400, 3200]
LVL_BAR = [20] + [120]*200

class PetConfig:
    """
    宠物配置
    """

    def __init__(self):

        self.petname = None
        self.width = 128
        self.height = 128
        self.scale = 1.0

        self.refresh = 5
        self.interact_speed = 0.02
        self.dropspeed = 1.0
        #self.gravity = 4.0

        self.default = None
        self.up = None
        self.down = None
        self.left = None
        self.right = None
        self.drag = None
        self.fall = None
        self.on_floor = None
        self.focus = None
        self.patpat = None
        #self.subpet = []
        self.act_dict = {}
        self.random_act = []
        self.act_prob = []
        self.act_name = []
        self.act_type = []
        self.act_sound = []
        #self.mouseDecor = {}
        self.accessory_act = {}
        self.acc_name = []
        self.custom_act = {}

        #self.hp_interval = 15
        #self.fv_interval = 15

        self.item_favorite = []
        self.item_dislike = []


    @classmethod
    def init_config(cls, pet_name: str, pic_dict: dict):

        path = os.path.join(basedir, 'res/role/{}/pet_conf.json'.format(pet_name))
        with open(path, 'r', encoding='UTF-8') as f:
            o = PetConfig()
            conf_params = json.load(f)

            o.petname = pet_name
            o.scale = conf_params.get('scale', 1.0)
            o.width = conf_params.get('width', 128) * o.scale
            o.height = conf_params.get('height', 128) * o.scale

            o.refresh = conf_params.get('refresh', 5)
            o.interact_speed = conf_params.get('interact_speed', 0.02) * 1000
            o.dropspeed = conf_params.get('dropspeed', 1.0) #not needed in v0.15+

            # 初始化所有动作
            act_path = os.path.join(basedir, 'res/role/{}/act_conf.json'.format(pet_name))
            act_conf = dict(json.load(open(act_path, 'r', encoding='UTF-8')))
            act_dict = {}
            act_dict = {k: Act.init_act(v, pic_dict, o.scale, pet_name, 'role', k) for k, v in act_conf.items()}
            o.act_dict = act_dict
            # 载入默认动作
            o.default = act_dict[conf_params['default']]
            o.up = act_dict[conf_params.get('up', 'default')]
            o.down = act_dict[conf_params.get('down', 'default')]
            o.left = act_dict[conf_params.get('left', 'default')]
            o.right = act_dict[conf_params.get('right', 'default')]
            o.drag = act_dict[conf_params['drag']]
            o.fall = act_dict[conf_params['fall']]
            o.prefall = act_dict[conf_params.get('prefall','fall')]
            o.on_floor = act_dict[conf_params.get('on_floor', 'default')]
            o.focus = act_dict[conf_params['focus']] if 'focus' in conf_params.keys() else None

            pat_conf = conf_params.get('patpat', 'default')
            if isinstance(pat_conf, str):
                # only a single action defined for pat
                pat_conf = dict([(i,pat_conf) for i in range(num_hp_states)])
            elif isinstance(pat_conf, dict):
                # pat animation defined separately for each HP tier
                pat_conf = fill_missing_hptier(pat_conf)
            else:
                # in case anything unexpected happens
                pat_conf = dict([(i, 'default') for i in range(num_hp_states)])

            o.patpat = dict([(i, act_dict[pat_conf[i]]) for i in range(num_hp_states)])

            # subpet now is independent from character

            
            # 初始化随机动作
            random_act = []
            act_prob = []
            act_name = []
            act_type = []
            act_sound = []

            for act_array in conf_params['random_act']:
                random_act.append([act_dict[act] for act in act_array['act_list']])
                act_prob.append(act_array.get('act_prob', 0.2))
                act_name.append(act_array.get('name', None))
                act_type.append(act_array.get('act_type', [2,1]))
                act_sound.append(act_array.get('sound', []))

            o.random_act = random_act
            if sum(act_prob) == 0:
                o.act_prob = [0] * len(act_prob)
            else:
                o.act_prob = [i/sum(act_prob) for i in act_prob]
            o.act_name = act_name
            o.act_type = act_type
            o.act_sound = act_sound


            # 初始化组件动作
            accessory_act = {}
            acc_name = []
            
            for acc_array in conf_params.get("accessory_act", []):
                act_list = [act_dict[act] for act in acc_array['act_list']]
                acc_list = [act_dict[act] for act in acc_array['acc_list']]
                acc_array['act_list'] = act_list
                acc_array['acc_list'] = acc_list
                acc_array['anchor'] = [i*o.scale for i in acc_array.get('anchor', [0,0])]
                acc_array['sound'] = acc_array.get('sound', [])

                accessory_act[acc_array['name']] = acc_array
                acc_name.append(acc_array['name'])

            o.accessory_act = accessory_act
            o.acc_name = acc_name

            o.custom_act = {}

            # 如果是附属宠物 其和主宠物之间的交互 - v0.3.3 subpet loading switched to another method

            o.item_favorite = conf_params.get('item_favorite', {})
            o.item_dislike = conf_params.get('item_dislike', {})
            

            # 对话列表
            msg_file = os.path.join(basedir, 'res/role/{}/msg_conf.json'.format(pet_name))
            if os.path.isfile(msg_file):
                msg_data = dict(json.load(open(msg_file, 'r', encoding='UTF-8')))

                msg_dict = conf_params.get("msg_dict", {})
                for msg in msg_dict.keys():
                    msg_dict[msg] = msg_data[msg_dict[msg]]

                o.msg_dict = msg_dict
            else:
                o.msg_dict = {}

            # 金币自定义
            if conf_params.get('coin_config', {}):
                coin_config = conf_params.get('coin_config', {})
                coin_name_dict = coin_config.get('name', {})
                coin_name_dict['default'] = 'Coin'

                if coin_config.get('image', None):
                    img_path = os.path.join(basedir, f'res/role/{pet_name}', coin_config['image'])
                    image = _load_item_img(img_path)
                else:
                    image = None
                o.coin_config = {'name':coin_name_dict, 'image':image}
            else:
                o.coin_config = {}

            return o

    @classmethod
    def init_sys(cls, pic_dict: dict):
        path = os.path.join(basedir, 'res/role/sys/sys_conf.json')
        with open(path, 'r', encoding='UTF-8') as f:
            o = PetConfig()
            conf_params = json.load(f)

            o.petname = 'sys'
            o.scale = conf_params.get('scale', 1.0)

            # 初始化所有动作
            act_path = os.path.join(basedir, 'res/role/sys/act_conf.json')
            act_conf = dict(json.load(open(act_path, 'r', encoding='UTF-8')))
            act_dict = {}
            act_dict = {k: Act.init_act(v, pic_dict, o.scale, 'sys', 'role', k) for k, v in act_conf.items()}

            # 初始化组件动作
            accessory_act = {}
            acc_name = []
            
            for acc_array in conf_params.get("accessory_act", []):
                act_list = [act_dict[act] for act in acc_array['act_list']]
                acc_list = [act_dict[act] for act in acc_array['acc_list']]
                acc_array['act_list'] = act_list
                acc_array['acc_list'] = acc_list
                acc_array['anchor'] = [i*o.scale for i in acc_array['anchor']]
                accessory_act[acc_array['name']] = acc_array
                acc_name.append(acc_array['name'])

            o.accessory_act = accessory_act
            o.acc_name = acc_name

            # 鼠标挂件 - 暂时搁置

            return o

    @classmethod
    def init_subpet(cls, pet_name: str, pic_dict: dict):

        path = os.path.join(basedir, 'res/pet/{}/pet_conf.json'.format(pet_name))
        with open(path, 'r', encoding='UTF-8') as f:
            o = PetConfig()
            conf_params = json.load(f)

            o.petname = pet_name
            o.scale = conf_params.get('scale', 1.0)
            o.width = conf_params.get('width', 128) * o.scale
            o.height = conf_params.get('height', 128) * o.scale
            o.interact_speed = conf_params.get('interact_speed', 0.02) * 1000

            # 初始化所有动作
            act_path = os.path.join(basedir, 'res/pet/{}/act_conf.json'.format(pet_name))
            act_conf = dict(json.load(open(act_path, 'r', encoding='UTF-8')))
            act_dict = {}
            act_dict = {k: Act.init_act(v, pic_dict, o.scale, pet_name, 'pet', k) for k, v in act_conf.items()}

            # 载入默认动作
            o.default = act_dict[conf_params['default']]
            o.up = act_dict[conf_params.get('up', 'default')]
            o.down = act_dict[conf_params.get('down', 'default')]
            o.left = act_dict[conf_params.get('left', 'default')]
            o.right = act_dict[conf_params.get('right', 'default')]
            o.drag = act_dict[conf_params.get('drag', 'default')]
            o.fall = act_dict[conf_params.get('fall', 'default')]
            prefall = conf_params.get('prefall', 'fall')
            o.prefall = act_dict.get(prefall, conf_params['default'])
            o.on_floor = act_dict[conf_params.get('on_floor', 'default')]

            pat_conf = conf_params.get('patpat', 'default')
            if isinstance(pat_conf, str):
                # only a single action defined for pat
                pat_conf = dict([(i,pat_conf) for i in range(num_hp_states)])
            elif isinstance(pat_conf, dict):
                # pat animation defined separately for each HP tier
                pat_conf = fill_missing_hptier(pat_conf)
            else:
                # in case anything unexpected happens
                pat_conf = dict([(i, 'default') for i in range(num_hp_states)])

            o.patpat = dict([(i, act_dict[pat_conf[i]]) for i in range(num_hp_states)])

            # Subpet position arguments
            o.follow_main_x = conf_params.get('follow_main_x', True)
            o.follow_main_y = conf_params.get('follow_main_y', False)
            o.anchor_to_main = conf_params.get('anchor_to_main', [])
            
            # Subpet Buff to chars - v0.3.4 moved to item_config
            # o.buff_dict = conf_params.get('buff', {})
         
            # 初始化随机动作
            random_act = []
            act_prob = []
            act_name = []
            act_type = []
            act_sound = []

            for act_array in conf_params['random_act']:
                random_act.append([act_dict[act] for act in act_array['act_list']])
                act_prob.append(act_array.get('act_prob', 0.2))
                act_name.append(act_array.get('name', None))
                act_type.append(act_array.get('act_type', [2,1]))
                act_sound.append(act_array.get('sound', []))

            o.random_act = random_act
            if sum(act_prob) == 0:
                o.act_prob = [0] * len(act_prob)
            else:
                o.act_prob = [i/sum(act_prob) for i in act_prob]
            o.act_name = act_name
            o.act_type = act_type
            o.act_sound = act_sound

            # 和主宠物之间的交互
            o.main_interact = conf_params.get("main_interact", {})

            return o



def fill_missing_hptier(pat_dict):
    pat_dict = dict([(int(k),v) for k,v in pat_dict.items()])
    full_dict = dict([(i, None) for i in range(num_hp_states)])
    full_dict.update(pat_dict)

    first_available_key = min(pat_dict.keys())

    for key in range(first_available_key - 1, -1, -1):
        full_dict[key] = full_dict[key + 1]

    for key in range(first_available_key, num_hp_states):
        if full_dict[key] is None:
            full_dict[key] = full_dict[key - 1]

    return full_dict



def CheckCharFiles(folder):
    """ Check if the character files (under res/role/NAME/) are able to run with no potential error """
    """
    Status Code
        0: Success
        1: pet_conf.json broken or not exist
        2: act_conf.json broken or not exist
        3: action missing "images" attribute
        4: image files missing
        5: default action missing in pet_conf.json
        6: action called by pet_conf.json is missing from act_conf.json
    """
    # Check pet_conf.json and act_conf.json
    try:
        path = os.path.join(folder, 'pet_conf.json')
        pet_conf = json.load(open(path, 'r', encoding='UTF-8'))
    except:
        return 1, None

    try:
        path = os.path.join(folder, 'act_conf.json')
        act_conf = json.load(open(path, 'r', encoding='UTF-8'))
    except:
        return 2, None

    # Check if actions are well-defined, and no missing image files
    error_action = []
    missing_imgs = []
    for action, actDic in act_conf.items():
        if "images" not in actDic.keys():
            error_action.append(action)
            continue
        else:
            images = actDic['images']
            img_dir = os.path.normpath(os.path.join(folder, f'action/{images}'))
            list_images = glob.glob(f'{img_dir}_*.png')
            pattern = re.compile(rf"^{re.escape(images)}_(\d+)\.png$")
            matching_idx = sorted(
                [pattern.match(os.path.basename(file)).group(1) for file in list_images if pattern.match(os.path.basename(file))],
                key=lambda x: int(x)
            )
            padding_width = len(matching_idx[0])
            m = int(matching_idx[0])
            n = int(matching_idx[-1])
            expected_indices = set(range(m, n + 1))
            current_indices = set([int(i) for i in matching_idx])
            missing_indices = expected_indices - current_indices
            missing_indices_padded = sorted(f"{idx:0{padding_width}}" for idx in missing_indices)
            imgMissed = [f'{img_dir}_{i}.png' for i in missing_indices_padded]
            if imgMissed == []:
                pass
            else:
                missing_imgs += imgMissed

    if error_action != []:
        return 3, error_action

    if missing_imgs != []:
        return 4, missing_imgs

    # Check if required actions exist
    reqAct = ['default','drag','fall']
    missAct = [i for i in reqAct if i not in pet_conf.keys()]
    if missAct != []:
        return 5, missAct

    # Check action in pet_conf.json are all defined in act_conf
    actionsKey = ["default", "up", "down", "left", "right", "drag", "fall", "on_floor"]
    actions = [pet_conf[i] for i in actionsKey if i in pet_conf.keys()]

    if "patpat" in pet_conf.keys():
        pat_conf = pet_conf["patpat"]
        if isinstance(pat_conf, str):
            actions.append(pat_conf)
        elif isinstance(pat_conf, dict):
            actions += list(pat_conf.values())

    random_act = pet_conf.get("random_act",[])
    for rndAct in random_act:
        actions += rndAct.get("act_list",[])

    accessory_act = pet_conf.get("accessory_act",[])
    for accAct in accessory_act:
        actions += accAct.get("act_list",[])
        actions += accAct.get("acc_list",[])

    missingActions = [i for i in actions if i not in act_conf.keys()]
    if missingActions != []:
        return 6, missingActions
    
    # Check character items if any
    itemFolder = os.path.join(folder, 'items')
    if os.path.exists(itemFolder):
        statCode, errorList = checkItemMOD(itemFolder)
        if statCode:
            statCode += 6
            return statCode, errorList

    return 0, None




class Act:
    def __init__(self, images=(), act_name=None, act_num=1, need_move=False, direction=None, frame_move=10, frame_refresh=0.04, anchor=[0,0]):
        """
        动作
        :param images: 动作图像
        :param act_num 动作执行次数
        :param need_move: 是否需要移动
        :param direction: 移动方向
        :param frame_move 单帧移动距离
        :param frame_refresh 单帧刷新时间
        """
        self.images = images
        self.act_name = act_name
        self.act_num = act_num
        self.need_move = need_move
        self.direction = direction
        self.frame_move = frame_move
        self.frame_refresh = frame_refresh
        self.anchor = anchor

    @classmethod
    def init_act(cls, conf_param, pic_dict, scale, pet_name, resFolder='role', act_name=None):

        images = conf_param['images']
        img_dir = os.path.join(basedir, 'res/{}/{}/action'.format(resFolder, pet_name))
        list_images = glob.glob(f'{img_dir}/{images}_*.png')
        pattern = re.compile(rf"^{re.escape(images)}_(\d+)\.png$")
        matching_idx = sorted(
            [pattern.match(os.path.basename(file)).group(1) for file in list_images if pattern.match(os.path.basename(file))],
            key=lambda x: int(x)
        )
        img = []
        for i in matching_idx:
            img.append(pic_dict["%s_%s"%(images, i)])

        if scale != 1:
            img = [i.scaled(int(i.width() * scale), 
                            int(i.height() * scale),
                            aspectMode=Qt.KeepAspectRatio,
                            mode=Qt.SmoothTransformation) for i in img]

        act_num = conf_param.get('act_num', 1)
        need_move = conf_param.get('need_move', False)
        direction = conf_param.get('direction', None)
        frame_move = conf_param.get('frame_move', 10) * scale
        frame_refresh = conf_param.get('frame_refresh', 0.5)
        anchor = conf_param.get('anchor', [0,0])
        return Act(img, act_name, act_num, need_move, direction, frame_move, frame_refresh, anchor)
    
    def customized_copy(self, start_idx, end_idx, num_rep):
        imgs = self.images * int(self.act_num)
        imgs = imgs[start_idx:end_idx]
        return Act(imgs, self.act_name, num_rep, self.need_move, self.direction, self.frame_move, self.frame_refresh, self.anchor)


def tran_idx_img(start_idx: int, end_idx: int, pic_dict: dict) -> list:
    """
    转化坐标与图像
    :param start_idx: 开始坐标
    :param end_idx: 结束坐标
    :param pic_dict: 图像dict
    :return: 一个动作所有的图片list
    """
    res = []
    for i in range(start_idx, end_idx + 1):
        res.append(pic_dict[str(i)])
    return res

class EmptyAct:
    def __init__(self, num_images, frame_refresh):
        self.images = [QPixmap()]
        self.act_name = None
        self.act_num = num_images
        self.need_move = False
        self.direction = None
        self.frame_move = 0
        self.frame_refresh = frame_refresh
        self.anchor = [0,0]



"""
Customized Animation:
-------------------------------------------------------------
"ACTNAME": {
    "act_type": "customized",
    "special_act": false,
    "unlocked": true,
    "in_playlist": true,
    "act_prob": 1.0,
    "status_type": [2, 1],
    "act_list": [["act2", 5, 16, 2], ["act3", 0, 20, 5]],
    "acc_list": [null, ["acc0", 0, 20, 5]],
    "anchor_list": [null, [-445,-501]]
}

-------------------------------------------------------------
act_list: List of List. Each List is a act defined in res/role/PETNAME/act_config.json
The elements are:
    - act name
    - act start img index
    - act end img index
    - number of repetition

Please note, start and end are not the original img file index!
It is already multiplied by `act_num`. For example,
This is an act defined in act_conf.json:
"shakehand": {
    "images": "sh",
    "act_num": 3,
    "frame_refresh": 0.06
}
And we have 4 images of sh_{}.png.
The index range of this act defined in data/act_data.json is: [0, 12]
And when users use it to define customized animation in the UI Panel, 
it makes sense to save and use the index data.

! This also means when design accessory animation, 
make sure the `frame_refresh` are the same for the set of act and acc.

-------------------------------------------------------------
Sometimes we have [60, 58] in the `act_list` and `acc_list`:
    - 60 means 60ms blank, not showing anything
    - 58 is the repetition
It is designed to keep act and acc at the same pace (synergic)

-------------------------------------------------------------
acc_list is defined similar to act_list, but keeps the accessory actions, which will be sent to QAccessory
anchor_list is the anchor of each accessory action
"""

class ActData:
    """
    Animation configuration data structure
    """

    def __init__(self, petsList):
        self.petsList = petsList
        self.current_pet = petsList[0]
        self.file_path = os.path.join(configdir, 'data/act_data.json')
        self.allAct_params = self.init_config()

    def init_config(self):
        if os.path.isfile(self.file_path):
            # Check file integrity
            try:
                allAct_params = json.load(open(self.file_path, 'r', encoding='UTF-8'))
                self.fileGood = True
            except:
                #File broken
                allAct_params = {}
                self.fileGood = False
        else:
            allAct_params = {}
            self.fileGood = True
        return allAct_params

    def init_actData(self, petname, hp_tier):
        self.current_pet = petname
        if self.current_pet not in self.allAct_params.keys():
            act_params = self.generate_config(self.current_pet)
        else:
            act_params = self.allAct_params[self.current_pet]
            act_params = self._check_actlist(petname, act_params)

        self.allAct_params[self.current_pet] = act_params
        self.save_data()

    def _check_actlist(self, petname, act_params):
        pet_conf_file = os.path.join(basedir, 'res/role/{}/pet_conf.json'.format(petname))
        pet_conf = json.load(open(pet_conf_file, 'r', encoding='UTF-8'))
        all_names_in_conf = []
        for act_conf in pet_conf.get('random_act', []):
            if act_conf['name'] not in act_params:
                act_params[act_conf['name']] = self._get_act_config(act_conf, 'random_act')
            all_names_in_conf.append(act_conf['name'])

        for act_conf in pet_conf.get('accessory_act', []):
            if act_conf['name'] not in act_params:
                act_params[act_conf['name']] = self._get_act_config(act_conf, 'accessory_act')
            all_names_in_conf.append(act_conf['name'])

        act_params = {key: value for key, value in act_params.items() if key in all_names_in_conf or value['act_type']=='customized'}

        return act_params

    def save_data(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.allAct_params, f, ensure_ascii=False, indent=4, separators=(',', ':'))

    def generate_config(self, pet_name):
        pet_conf_file = os.path.join(basedir, 'res/role', pet_name, 'pet_conf.json')
        pet_conf = json.load(open(pet_conf_file, 'r', encoding='UTF-8'))
        act_params = {}
        for actset in pet_conf.get("random_act", []):
            act_params[actset['name']] = self._get_act_config(actset, "random_act")

        for accset in pet_conf.get("accessory_act", []):
            act_params[accset['name']] = self._get_act_config(accset, "accessory_act")

        return act_params

    def _get_act_config(self, actset, act_type):
        status_type = actset.get('status_type', [2,0])
        follow_mouse = actset.get('follow_mouse', False)
        unlocked = True

        if follow_mouse:
            act_prob = 0
        else:
            act_prob = actset.get('act_prob', 1.0)

        return {
                "act_type": act_type,
                "special_act": follow_mouse,
                "unlocked": unlocked,
                "in_playlist": unlocked,
                "act_prob": act_prob,
                "status_type": status_type
                }



class PetData:
    """
    宠物数据创建、读取、存储 (精简版)
    仅保留: current_pet, days, last_opened
    """

    def __init__(self, petsList):

        self.frozen_data = False

        # 精简版: 添加stub属性以兼容旧代码
        self.hp = 100
        self.hp_tier = 3
        self.fv = 0
        self.fv_lvl = 0
        self.items = {}
        self.coins = 0

        self.file_path = os.path.join(configdir, 'data/pet_data.json')
        self.petsList = petsList
        self.current_pet = petsList[0]

        self.init_data()

    def init_data(self):

        if os.path.isfile(self.file_path):
            # Check file integrity
            try:
                allData_params = json.load(open(self.file_path, 'r', encoding='UTF-8'))
                self.saveGood = True
            except:
                # File broken
                allData_params = {}
                self.saveGood = False

            if self.current_pet not in allData_params.keys():
                # 需要迁移旧数据或创建新数据
                allData_params = self._migrate_to_lite(allData_params)
        else:
            # First time using the App
            self.saveGood = True
            allData_params = {}
            now = datetime.now()
            for pet in self.petsList:
                allData_params[pet] = self._create_default_data()

        data_params = allData_params[self.current_pet]
        self.days = data_params['days']
        self.last_opened = data_params['last_opened']
        allData_params[self.current_pet] = data_params.copy()

        self.allData_params = allData_params

        self.save_data()
        self.value_type = {key: type(data_params[key]) for key in data_params.keys()}

    def _create_default_data(self):
        """创建默认数据"""
        now = datetime.now()
        return {
            'days': 1,
            'last_opened': '%i-%i-%i' % (now.year, now.month, now.day)
        }

    def _migrate_to_lite(self, old_data: dict) -> dict:
        """迁移到精简版，丢弃HP/FV/物品/金币数据"""
        new_data = {}
        now = datetime.now()
        default_data = self._create_default_data()

        # 检查是否是旧版本格式 (包含HP字段)
        if 'HP' in old_data.keys():
            # 旧版本 - 需要为每个宠物创建新数据
            for pet in self.petsList:
                new_data[pet] = default_data.copy()
        else:
            # 新版本但缺少当前宠物
            for pet in self.petsList:
                if pet in old_data.keys():
                    # 保留days和last_opened，丢弃其他
                    new_data[pet] = {
                        'days': old_data[pet].get('days', 1),
                        'last_opened': old_data[pet].get('last_opened', '%i-%i-%i' % (now.year, now.month, now.day))
                    }
                else:
                    new_data[pet] = default_data.copy()

        return new_data

    def _sumDays(self, data_params):
        if 'days' in data_params and 'last_opened' in data_params:
            days = data_params['days']
            now = datetime.now()
            lp = data_params['last_opened'].split('-')
            last_opened = datetime(year=int(lp[0]), month=int(lp[1]), day=int(lp[2]),
                                   hour=now.hour, minute=now.minute, second=now.second)
            if (now - last_opened).days == 0:
                # 同一天重复打开
                days = days
                last_opened = '%i-%i-%i' % (now.year, now.month, now.day)
            else:
                days = days + 1
                last_opened = '%i-%i-%i' % (now.year, now.month, now.day)
        else:
            # 初次统计陪伴时间
            ct = os.path.getctime(self.file_path)
            ct = time.strptime(time.ctime(ct))
            ct = time.strftime("%Y-%m-%d", ct).split('-')

            now = datetime.now()
            ct = datetime(year=int(ct[0]), month=int(ct[1]), day=int(ct[2]),
                          hour=now.hour, minute=now.minute, second=now.second)
            time_diff = now - ct
            days = time_diff.days + 1
            last_opened = '%i-%i-%i' % (now.year, now.month, now.day)

        return days, last_opened

    def _change_pet(self, current_pet):
        self.current_pet = current_pet

        if current_pet not in self.allData_params.keys():
            now = datetime.now()
            self.allData_params[self.current_pet] = self._create_default_data()

        data_params = self.allData_params[self.current_pet]
        self.days, self.last_opened = self._sumDays(data_params)
        data_params['days'] = self.days
        data_params['last_opened'] = self.last_opened
        self.allData_params[self.current_pet] = data_params.copy()

        self.save_data()

    def update_date(self):
        self.days, self.last_opened = self._sumDays(self.allData_params[self.current_pet])
        self.allData_params[self.current_pet]['days'] = self.days
        self.allData_params[self.current_pet]['last_opened'] = self.last_opened
        self.save_data()

    def save_data(self):
        if self.frozen_data:
            return

        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.allData_params, f, ensure_ascii=False, indent=4)

    def check_save_integrity(self, save_allDict, petname):
        """检查存档完整性"""
        required_keys = {'days', 'last_opened'}

        if petname == 'all':
            for pet, save_dict in save_allDict.items():
                if not required_keys.issubset(save_dict.keys()):
                    return 0
            return 1
        else:
            save_dict = save_allDict.get(petname, None)
            if save_dict is None:
                return 0
            return 1 if required_keys.issubset(save_dict.keys()) else 0

    def transfer_save(self, save_allDict, petname, days_info=False):
        """导入存档"""
        try:
            if petname == 'all':
                for pet, save_dict in save_allDict.items():
                    self._transfer_save_toPet(save_dict, pet)
            else:
                save_dict = save_allDict.get(petname, None)
                if not save_dict:
                    return 0
                self._transfer_save_toPet(save_dict, petname)
        except:
            return 0

        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.allData_params, f, ensure_ascii=False, indent=4)
        return 1

    def _transfer_save_toPet(self, data_params, petname):
        """将数据转移到指定宠物"""
        if petname in self.allData_params.keys():
            self.allData_params[petname]['days'] = data_params.get('days', 1)
            self.allData_params[petname]['last_opened'] = data_params.get('last_opened', '')

        if petname not in self.allData_params.keys():
            self.allData_params[petname] = data_params.copy()
        else:
            days, last_opened = self.allData_params[petname]['days'], self.allData_params[petname]['last_opened']
            self.allData_params[petname] = data_params.copy()
            self.allData_params[petname]['days'] = days
            self.allData_params[petname]['last_opened'] = last_opened

        if petname == self.current_pet:
            data_params = self.allData_params[self.current_pet]
            self.hp = data_params['HP']
            self.hp_tier = data_params['HP_tier']
            self.fv = data_params['FV']
            self.fv_lvl = data_params['FV_lvl']
            self.items = data_params['items']
            self.coins = data_params['coins']
            self.days = data_params['days']
            self.last_opened = data_params['last_opened']


    def frozen(self):
        self.frozen_data = True






class TaskData:
    """
    Data about daily task

    Task Data
    -------------
        history
            History record: List. ('Date', 'Minutes')
        goal
            daily focus time (minute) goal: int
        goal_completed
            bool indicates if daily goal already completed
        n_days
            Number of completed days-in-a-row: int
        tasks_todo
            Dict of task_id: task_text
        tasks_done
            Dict of task_id: task_text
        n_tasks
            Number of completed tasks: int
    

    TO-DO: What if day changed while App is running?
    """

    def __init__(self):
        """
        Task Data Init
        Load / Create task data file
        """

        self.file_path = os.path.join(configdir, 'data/task_data.json')
        self.init_data()
        self.save_data()


    def init_data(self):
        # Load in data
        if os.path.isfile(self.file_path):
            # Check file integrity
            try:
                self.taskData = json.load(open(self.file_path, 'r', encoding='UTF-8'))
                self.stateGood = True
            except:
                #File broken (seen by a few users)
                self.taskData = self._createData()
                self.stateGood = False

        else:
            self.taskData = self._createData()
            self.stateGood = True

        # Check data integrity
        self.taskData = self._checkData(self.taskData)

        # Check if first time open today
        self.checkDate()
        


    def _createData(self):
        return {'history': [],
                'goal': 180,
                'goal_completed': False,
                'n_days': 0,
                'tasks_todo': {},
                'tasks_done': {},
                'n_tasks': 0}


    def _checkData(self, taskData):
        empty_data = self._createData()
        for k in empty_data.keys():
            if k not in taskData:
                taskData[k] = empty_data[k]

            elif type(taskData[k]) != type(empty_data[k]):
                taskData[k] = empty_data[k]

        return taskData


    def _check_Date(self):
        """ return today_exist, yesterday_exist """
        today_exist, yesterday_exist = False, False
        now = datetime.now()
        self.today = f"{now.year}-{now.month}-{now.day}"
        if self.taskData['history']:
            lp = self.taskData['history'][-1][0].split('-')
            last_opened = datetime(year=int(lp[0]), month=int(lp[1]), day=int(lp[2]),
                                   hour=now.hour, minute=now.minute, second=now.second)
        
            if (now - last_opened).days == 0:
                # Opened in the same day
                today_exist = True
                if len(self.taskData['history']) >= 2:
                    last_2nd = self.taskData['history'][-2][0].split('-')
                    last_2nd_opened = datetime(year=int(last_2nd[0]), month=int(last_2nd[1]), day=int(last_2nd[2]),
                                           hour=now.hour, minute=now.minute, second=now.second)
                    if (now - last_2nd_opened).days == 1:
                        yesterday_exist = True
                    else:
                        yesterday_exist = False
                else:
                    yesterday_exist = False

            elif (now - last_opened).days == 1:
                today_exist, yesterday_exist = False, True
            else:
                today_exist, yesterday_exist = False, False

        return today_exist, yesterday_exist


    def save_data(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.taskData, f, ensure_ascii=False, indent=4)


    def checkDate(self):
        today_exist, yesterday_exist = self._check_Date()
        if not today_exist:
            self.taskData['history'].append((self.today, 0))
            self.taskData['goal_completed'] = False
        if not yesterday_exist:
            self.yesterday = 0
        else:
            self.yesterday = self.taskData['history'][-2][1]

        if self.yesterday < self.taskData['goal'] and not today_exist:
            self.taskData['n_days'] = 0

    def update_progress(self, newVal):
        date_str = self.taskData['history'][-1][0]
        self.taskData['history'][-1] = (date_str, newVal)


# 精简版: 物品系统已移除，提供空类和函数避免导入错误


class ItemData:
    """物品数据 (精简版 - 已移除)"""

    def __init__(self, HUNGERSTR='Satiety', FAVORSTR='Favorability'):
        self.item_dict = {}
        self.reward_dict = {}
        self.coin = {'name': {'default': 'Coin'}, 'image': None}
        self.default_coin = self.coin.copy()


def load_ItemMod(configPath, HUNGERSTR='Satiety', FAVORSTR='Favorability'):
    """物品配置加载 (精简版 - 已移除)"""
    return {}
