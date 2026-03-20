import sys
import time
import random
import math
import uuid
import types
import inspect
from typing import List

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction

from ClawPet.utils import *
from ClawPet.config import *

import ClawPet.settings as settings
basedir = settings.BASEDIR


##############################
#       Animation Module
##############################

class Animation_worker(QObject):
    sig_setimg_anim = Signal(name='sig_setimg_anim')
    sig_move_anim = Signal(float, float, name='sig_move_anim')
    sig_repaint_anim = Signal()
    acc_regist = Signal(dict, name='acc_regist')

    def __init__(self, pet_conf, parent=None):
        """
        Animation Module (精简版)
        Display user-defined animations randomly
        :param pet_conf: PetConfig class object in Main Widgets
        """
        super(Animation_worker, self).__init__(parent)
        self.pet_conf = pet_conf
        # 精简版: 不再使用HP/FV状态
        self.current_status = [3, 0]  # 默认状态
        self.nonDefault_prob = 0.25  # 简化概率
        self.act_cmlt_prob = self._cal_prob()
        self.is_killed = False
        self.is_paused = False


    def run(self):
        """Run animation in a separate thread"""
        print('start running pet %s'%(self.pet_conf.petname))
        time.sleep(5)
        while not self.is_killed:
            #if self.is_hp:
            self.random_act()

            while self.is_paused:
                time.sleep(0.2)
            if self.is_killed:
                break

            #time.sleep(self.pet_conf.refresh)

    def kill(self):
        self.is_paused = False
        self.is_killed = True

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def update_prob(self):
        # 精简版: 不再根据HP/FV更新概率
        self.act_cmlt_prob = self._cal_prob()

    def _cal_prob(self):
        """精简版: 简化概率计算，不使用HP/FV状态"""
        act_conf = settings.act_data.allAct_params[settings.petname]
        act_name = [k for k, v in act_conf.items()]
        act_prob = [act_conf[k]['act_prob'] for k in act_name]
        act_unlocked = [act_conf[k]['unlocked'] for k in act_name]
        act_inlist = [act_conf[k]['in_playlist'] for k in act_name]

        new_prob = []
        for i in range(len(act_name)):
            if not act_unlocked[i] or not act_inlist[i]:
                new_prob.append(0)
            else:
                new_prob.append(act_prob[i])

        if sum(new_prob) != 0:
            new_prob = [i / sum(new_prob) for i in new_prob]
            total = 0
            act_cmlt_prob = []
            for i in range(len(new_prob)):
                total += new_prob[i]
                act_cmlt_prob.append(total)
            act_cmlt_prob[-1] = 1.0
        else:
            act_cmlt_prob = [0] * len(new_prob)

        act_cmlt_prob = [round(i,3) for i in act_cmlt_prob]
        return act_cmlt_prob

    def random_act(self) -> None:
        """
        随机执行动作
        :return:
        """
        acts = None
        accs = None
        # If HP type is not starving, this condition also makes sure only starving animation is played

        # If under focus timer, play focus animation
        if settings.focus_timer_on and self.pet_conf.focus:
            acts = [self.pet_conf.focus]

        # If there is only 1 animation, select the default animation mode
        elif set(self.act_cmlt_prob) == set([0,1]):
            act_idx = sum([i < 1.0 for i in self.act_cmlt_prob])
            act_name = list(settings.act_data.allAct_params[settings.petname].keys())[act_idx]
            acts, accs = self._get_acts(act_name)

        # Else random animation mode
        else:
            prob_num_0 = random.uniform(0, 1)
            # Random animation not selected, play default
            if prob_num_0 > self.nonDefault_prob:
                acts = [self.pet_conf.default]
            # Random animation selected
            else:
                prob_num = random.uniform(0, 1)
                act_idx = sum([ i < prob_num for i in self.act_cmlt_prob])
                # In some situation, no animation is selected (e.g., there is no random animation)
                if act_idx >= len(self.act_cmlt_prob):
                    acts = [self.pet_conf.default]
                else:
                    act_name = list(settings.act_data.allAct_params[settings.petname].keys())[act_idx]
                    acts, accs = self._get_acts(act_name)

        self._run_acts(acts, accs)


    def _get_acts(self, act_name):
        act_conf = settings.act_data.allAct_params[settings.petname][act_name]
        act_type = act_conf['act_type']
        if act_type == 'random_act':
            act_index = self.pet_conf.act_name.index(act_name)
            acts = self.pet_conf.random_act[act_index]
            accs = None

        elif act_type == 'accessory_act':
            acts = self.pet_conf.accessory_act[act_name]['act_list']
            accs = {'acc_list': self.pet_conf.accessory_act[act_name]['acc_list'],
                    'anchor': self.pet_conf.accessory_act[act_name]['anchor'],
                    'follow_main': self.pet_conf.accessory_act[act_name].get('follow_main', False),
                    'speed_follow_main': self.pet_conf.accessory_act[act_name].get('speed_follow_main', 5),
                    'follow_mouse': self.pet_conf.accessory_act[act_name].get('follow_mouse', False)}
        elif act_type == 'customized':
            acts = self.pet_conf.custom_act[act_name]['act_list']
            if self.pet_conf.custom_act[act_name]['acc_list']:
                accs = {'acc_list': self.pet_conf.custom_act[act_name]['acc_list'],
                        'anchor': self.pet_conf.custom_act[act_name]['anchor'],
                        'name': 'customized_acc' # For Accessory module to judge the type
                        }
            else:
                accs = None
        else:
            acts = None
            accs = None

        return acts, accs


    def _run_acts(self, acts: List[Act], accs: List[Act] = None) -> None:
        """
        执行动画, 将一个动作相关的图片循环展示
        :param acts: 一组关联动作
        :return:
        """
        #start = time.time()
        if accs:
            self.acc_regist.emit(accs)
        for act in acts:
            self._run_act(act)
        #self.is_run_act = False

    def _run_act(self, act: Act) -> None:
        """
        加载图片执行移动
        :param act: 动作
        :return:
        """
        # if this is a skipping act
        if isinstance(act, list):
            for i in range(act[1]):
                if self.is_paused:
                    break
                if self.is_killed:
                    break
                time.sleep(act[0]/1000)
            return

        for i in range(act.act_num):

            #while self.is_paused:
            #    time.sleep(0.2)
            if self.is_paused:
                break
            if self.is_killed:
                break

            for img in act.images:

                #while self.is_paused:
                #    time.sleep(0.2)
                if self.is_paused:
                    break
                if self.is_killed:
                    break

                #global current_img, previous_img
                settings.previous_img = settings.current_img
                settings.current_img = img
                settings.previous_anchor = settings.current_anchor
                settings.current_anchor =  [int(i * settings.tunable_scale) for i in act.anchor]
                self.sig_setimg_anim.emit()
                #time.sleep(act.frame_refresh) ######## sleep 和 move 是不是应该反过来？
                #if act.need_move:
                self._move(act) #self.pos(), act)
                time.sleep(act.frame_refresh)
                #else:
                #    self._static_act(self.pos())
                self.sig_repaint_anim.emit()
    '''
    def _static_act(self, pos: QPoint) -> None:
        """
        静态动作判断位置 - 目前舍弃不用
        :param pos: 位置
        :return:
        """
        screen_geo = QDesktopWidget().screenGeometry()
        screen_width = screen_geo.width()
        screen_height = screen_geo.height()
        border = self.pet_conf.size
        new_x = pos.x()
        new_y = pos.y()
        if pos.x() < border:
            new_x = screen_width - border
        elif pos.x() > screen_width - border:
            new_x = border
        if pos.y() < border:
            new_y = screen_height - border
        elif pos.y() > screen_height - border:
            new_y = border
        self.move(new_x, new_y)
    '''

    def _move(self, act: QAction) -> None: #pos: QPoint, act: QAction) -> None:
        """
        移动动作
        :param pos: 当前位置
        :param act: 动作
        :return
        """
        plus_x = 0.
        plus_y = 0.
        direction = act.direction
        if direction is None:
            pass
        else:
            if direction == 'right':
                plus_x = act.frame_move

            if direction == 'left':
                plus_x = -act.frame_move

            if direction == 'up':
                plus_y = -act.frame_move

            if direction == 'down':
                plus_y = act.frame_move
        if plus_x == 0 and plus_y == 0:
            pass
        else:
            self.sig_move_anim.emit(plus_x, plus_y)
