import sys
import time
import random
import math
import uuid
import types
import inspect
from typing import List

from PySide6.QtCore import Qt, QTimer, QObject, QPoint
from PySide6.QtGui import QImage, QPixmap, QIcon, QCursor, QAction, QTransform
from PySide6.QtWidgets import *
from PySide6.QtCore import QObject, QThread, Signal

from ClawPet.utils import *
from ClawPet.config import *

import ClawPet.settings as settings
basedir = settings.BASEDIR
sys_hp_tiers = settings.HP_TIERS
sys_nonDefault_prob = [1, 0.125, 0.25, 0.5]


##############################
#      Interaction Module
##############################

class Interaction_worker(QObject):

    sig_setimg_inter = Signal(name='sig_setimg_inter')
    sig_move_inter = Signal(float, float, name='sig_move_inter')
    #sig_repaint_inter = Signal()
    sig_act_finished = Signal()
    sig_interact_note = Signal(str, str, name='sig_interact_note')

    acc_regist = Signal(dict, name='acc_regist')
    query_position = Signal(str, name='query_position')
    stop_trackMouse = Signal(name='stop_trackMouse')

    def __init__(self, pet_conf, parent=None):
        """
        Interaction Module
        Respond immediately to signals and run functions defined

        pet_conf: PetConfig class object in Main Widgets

        """
        super(Interaction_worker, self).__init__(parent)
        self.pet_conf = pet_conf
        self.is_killed = False
        self.is_paused = False
        self.interact = None
        self.act_name = None # everytime making act_name to None, don't forget to set settings.playid to 0
        self.interact_altered = False
        self.hptier = sys_hp_tiers #[0, 50, 80, 100]
        self.pat_idx = None

        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(self.run)
        self.timer.start(self.pet_conf.interact_speed)
        #self.start = time.time()


    def run(self):
        #self.start = time.time()
        if self.interact is None:
            return
        elif self.interact not in dir(self):
            self.interact = None
        else:
            if self.interact_altered:
                self.empty_interact()
                self.interact_altered = False
            getattr(self,self.interact)(self.act_name)

    def _get_animation_type(self, act_name):
        act_conf = settings.act_data.allAct_params[settings.petname]
        if act_name not in act_conf:
            return None
        act_type = act_conf[act_name]['act_type']
        if act_type == 'random_act':
            return 'animat'

        elif act_type == 'accessory_act':
            return 'anim_acc'

        elif act_type == 'customized':
            return 'customized'

    def start_interact(self, interact, act_name=None):
        # If Act selected from menu/panel, judge animation type first
        if interact == "actlist":
            interact = self._get_animation_type(act_name)
            if not interact:
                self.stop_interact()
                return
            #elif interact == 'customized':
            #    self.stop_interact()
            #    return

        sound_list = []
        if interact == 'animat' and act_name in self.pet_conf.act_name:
            sound_list = self.pet_conf.act_sound[self.pet_conf.act_name.index(act_name)]
            hp_lvl = self.pet_conf.act_type[self.pet_conf.act_name.index(act_name)][0]

        elif interact == 'anim_acc' and act_name in self.pet_conf.acc_name:
            sound_list = self.pet_conf.accessory_act[act_name]['sound']
            hp_lvl = self.pet_conf.accessory_act[act_name]['act_type'][0]

        # Customized animation currently doesn't have sound

        if len(sound_list) > 0 and settings.pet_data.hp_tier >= hp_lvl:
            sound_name = random.choice(sound_list)
            self.sig_interact_note.emit(sound_name, '')

        self.interact_altered = True
        if interact == 'anim_acc' or interact == 'customized':
            self.first_acc = True

        if self.interact == 'followTarget':
            if self.act_name == 'mouse':
                self.stop_trackMouse.emit()

        # sample pat animation
        if interact == 'patpat':
            self.pat_idx = self.sample_pat_anim()
        self.interact = interact
        self.act_name = act_name

    def kill(self):
        self.is_paused = False
        self.is_killed = True
        #self.timer.stop()
        # terminate thread

    def pause(self):
        self.is_paused = True
        #self.timer.stop()

    def resume(self):
        self.is_paused = False

    def stop_interact(self):
        self.interact = None
        self.act_name = None
        self.first_acc = False
        settings.playid = 0
        settings.act_id = 0
        self.sig_act_finished.emit()

    def empty_interact(self):
        settings.playid = 0
        settings.act_id = 0

    def sample_pat_anim(self):
        # 精简版: 简化拍拍动画选择
        return 3  # 始终返回最高状态

    def img_from_act(self, act):

        if settings.current_act != act:
            settings.previous_act = settings.current_act
            settings.current_act = act
            settings.playid = 0

        # if this is a skipping act
        if isinstance(act, list):
            n_repeat = math.ceil(act[0]/self.pet_conf.interact_speed) * act[1]
            settings.playid += 1
            if settings.playid >= n_repeat:
                settings.playid = 0
        else:
            n_repeat = math.ceil(act.frame_refresh / (self.pet_conf.interact_speed / 1000))
            img_list_expand = [item for item in act.images for i in range(n_repeat)] * act.act_num
            img = img_list_expand[settings.playid]

            settings.playid += 1
            if settings.playid >= len(img_list_expand):
                settings.playid = 0
            settings.previous_img = settings.current_img
            settings.current_img = img
            settings.previous_anchor = settings.current_anchor
            settings.current_anchor = [int(i * settings.tunable_scale) for i in act.anchor]

    def animat(self, act_name):
        #if act_name == 'on_floor':

        #start = time.time()
        try:
            acts_index = self.pet_conf.act_name.index(act_name)
        except:
            self.stop_interact()
            return

        # 判断是否满足动作饱食度要求
        if settings.pet_data.hp_tier < self.pet_conf.act_type[acts_index][0]:
            message = f"[{act_name}]" + " " + self.tr("needs Satiety be larger than") + f" {self.hptier[self.pet_conf.act_type[acts_index][0]-1]}"
            self.sig_interact_note.emit('status_hp', message) #'[%s] 需要饱食度%i以上哦'%(act_name, self.hptier[self.pet_conf.act_type[acts_index][0]-1]))
            self.stop_interact()
            return

        acts = self.pet_conf.random_act[acts_index]
        if settings.act_id >= len(acts):
            #settings.act_id = 0
            #self.interact = None
            self.stop_interact()
            #self.sig_act_finished.emit()
        else:
            act = acts[settings.act_id]
            n_repeat = math.ceil(act.frame_refresh / (self.pet_conf.interact_speed / 1000))
            n_repeat *= len(act.images) * act.act_num
            self.img_from_act(act)
            if settings.playid >= n_repeat-1:
                settings.act_id += 1

            if act_name == 'onfloor' and settings.fall_right:
                settings.previous_img = settings.current_img
                transform = QTransform()
                transform.scale(-1, 1)
                settings.current_img = settings.current_img.transformed(transform) #.mirrored(True, False)
                settings.current_anchor = [int(i * settings.tunable_scale) for i in act.anchor]
                settings.current_anchor = [-settings.current_anchor[0], settings.current_anchor[1]]

            if settings.previous_img != settings.current_img or settings.previous_anchor != settings.current_anchor:
                self.sig_setimg_inter.emit()
                self._move(act)

    def anim_acc(self, acc_name):

        # 判断是否满足动作饱食度要求
        if settings.pet_data.hp_tier < self.pet_conf.accessory_act[acc_name]['act_type'][0]:
            message = f"[{acc_name}]" + " " + self.tr("needs Satiety be larger than") + f" {self.hptier[self.pet_conf.accessory_act[acc_name]['act_type'][0]-1]}"
            self.sig_interact_note.emit('status_hp', message) #'[%s] 需要饱食度%i以上哦'%(acc_name, self.hptier[self.pet_conf.accessory_act[acc_name]['act_type'][0]-1]))
            self.stop_interact()
            return

        if self.first_acc:
            accs = self.pet_conf.accessory_act[acc_name]
            self.acc_regist.emit(accs)
            self.first_acc = False

        acts = self.pet_conf.accessory_act[acc_name]['act_list']

        if settings.act_id >= len(acts):
            #settings.act_id = 0
            #self.interact = None
            self.stop_interact()
            #self.sig_act_finished.emit()
        else:
            act = acts[settings.act_id]
            n_repeat = math.ceil(act.frame_refresh / (self.pet_conf.interact_speed / 1000))
            n_repeat *= len(act.images) * act.act_num
            self.img_from_act(act)
            if settings.playid >= n_repeat-1:
                settings.act_id += 1

            if settings.previous_img != settings.current_img or settings.previous_anchor != settings.current_anchor:
                self.sig_setimg_inter.emit()
                self._move(act)

    def customized(self, act_name):

        # 判断是否满足动作饱食度要求
        if settings.pet_data.hp_tier < self.pet_conf.custom_act[act_name]['act_type'][0]:
            message = f"[{act_name}]" + " " + self.tr("needs Satiety be larger than") + f" {self.hptier[self.pet_conf.custom_act[act_name]['act_type'][0]-1]}"
            self.sig_interact_note.emit('status_hp', message)
            self.stop_interact()
            return

        if self.first_acc:
            if self.pet_conf.custom_act[act_name]['acc_list']:
                accs = {'acc_list': self.pet_conf.custom_act[act_name]['acc_list'],
                        'anchor': self.pet_conf.custom_act[act_name]['anchor'],
                        'name': 'customized_acc' # For Accessory module to judge the type
                        }
                self.acc_regist.emit(accs)
            self.first_acc = False

        acts = self.pet_conf.custom_act[act_name]['act_list']

        if settings.act_id >= len(acts):
            #settings.act_id = 0
            #self.interact = None
            self.stop_interact()
            #self.sig_act_finished.emit()
        else:
            act = acts[settings.act_id]
            # if this is a skipping act
            if isinstance(act, list):
                n_repeat = math.ceil(act[0]/self.pet_conf.interact_speed) * act[1]
            else:
                n_repeat = math.ceil(act.frame_refresh / (self.pet_conf.interact_speed / 1000))
                n_repeat *= len(act.images) * act.act_num
            self.img_from_act(act)
            if settings.playid >= n_repeat-1:
                settings.act_id += 1

            if settings.previous_img != settings.current_img or settings.previous_anchor != settings.current_anchor:
                self.sig_setimg_inter.emit()
                self._move(act)

    def patpat(self, act_name):
        acts = [self.pet_conf.patpat[self.pat_idx]]
        if settings.act_id >= len(acts):
            #settings.act_id = 0
            #self.interact = None
            self.stop_interact()
            #self.sig_act_finished.emit()
        else:
            act = acts[settings.act_id]
            n_repeat = math.ceil(act.frame_refresh / (self.pet_conf.interact_speed / 1000))
            n_repeat *= len(act.images) * act.act_num
            self.img_from_act(act)
            if settings.playid >= n_repeat-1:
                settings.act_id += 1

            if settings.previous_img != settings.current_img or settings.previous_anchor != settings.current_anchor:
                self.sig_setimg_inter.emit()
                self._move(act)

    def mousedrag(self, act_name):

        # Falling is OFF
        if not settings.set_fall:
            if settings.draging==1:
                acts = self.pet_conf.drag

                self.img_from_act(acts)
                if settings.previous_img != settings.current_img or settings.previous_anchor != settings.current_anchor:
                    self.sig_setimg_inter.emit()

            else:
                self.stop_interact()
                #self.interact = None
                #self.act_name = None
                #settings.playid = 0

        # Falling is ON
        elif settings.set_fall==1 and settings.onfloor==0:
            if settings.draging==1:
                acts = self.pet_conf.drag
                self.img_from_act(acts)
                if settings.previous_img != settings.current_img or settings.previous_anchor != settings.current_anchor:
                    self.sig_setimg_inter.emit()

            elif settings.draging==0:
                if settings.prefall == 1:
                    acts = self.pet_conf.prefall
                else:
                    acts = self.pet_conf.fall

                n_repeat = math.ceil(acts.frame_refresh / (self.pet_conf.interact_speed / 1000))
                n_repeat *= len(acts.images) * acts.act_num

                self.img_from_act(acts)
                if settings.playid >= n_repeat-1:
                    settings.prefall = 0

                #global fall_right
                if settings.fall_right:
                    settings.previous_img = settings.current_img
                    transform = QTransform()
                    transform.scale(-1, 1)
                    settings.current_img = settings.current_img.transformed(transform)
                    settings.current_anchor = [int(i * settings.tunable_scale) for i in acts.anchor]
                    settings.current_anchor = [-settings.current_anchor[0], settings.current_anchor[1]]

                if settings.previous_img != settings.current_img or settings.previous_anchor != settings.current_anchor:
                    self.sig_setimg_inter.emit()

                self.drop()

        else:
            #self.stop_interact()
            #self.interact = 'animat' #None
            #self.act_name = 'onfloor' #None
            self.start_interact('animat', 'onfloor')
            #settings.playid = 0
            #settings.act_id = 0

        #self.sig_repaint_inter.emit()


        #elif set_fall==0 and onfloor==0:

    def drop(self):
        #掉落

        #dropnext=pettop+info.gravity*dropa-info.gravity/2
        plus_y = settings.dragspeedy #+ self.pet_conf.dropspeed
        plus_x = settings.dragspeedx
        settings.dragspeedy = settings.dragspeedy + settings.gravity

        self.sig_move_inter.emit(plus_x, plus_y)

    def _move(self, act: QAction) -> None: #pos: QPoint, act: QAction) -> None:
        """
        在 Thread 中发出移动Signal
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

        #self.sig_move_inter.emit(plus_x, plus_y)
        if plus_x == 0 and plus_y == 0:
            pass
        else:
            self.sig_move_inter.emit(plus_x, plus_y)

    def use_item(self, item):
        # 宠物进行 三个等级的喂食动画
        if item in self.pet_conf.item_favorite:
            self.start_interact('animat','feed_1')
        elif item in self.pet_conf.item_dislike:
            self.start_interact('animat','feed_3')
        else:
            self.start_interact('animat','feed_2')

        '''
        self.interact = 'animat' #None
        self.act_name = 'onfloor' #None
        settings.playid = 0
        settings.act_id = 0
        '''
        #self.stop_interact()
        return

    def use_clct(self, item):
        if item in self.pet_conf.act_name:
            self.start_interact('animat', item)
        elif item in self.pet_conf.acc_name:
            self.start_interact('anim_acc', item)
        else:
            self.stop_interact()

        return

    def followTarget(self, act_name):

        self.query_position.emit(act_name)
        distance = abs(self.main_pos[0] - self.target_pos[0])

        if distance < 5*self.pet_conf.left.frame_move:
            act = self.pet_conf.default
            self.img_from_act(act)
            if settings.previous_img != settings.current_img or settings.previous_anchor != settings.current_anchor:
                self.sig_setimg_inter.emit()

        else:
            act = [self.pet_conf.left, self.pet_conf.right][int(self.main_pos[0] < self.target_pos[0])]
            self.img_from_act(act)
            if settings.previous_img != settings.current_img or settings.previous_anchor != settings.current_anchor:
                self.sig_setimg_inter.emit()
                self._move(act)


    def receive_pos(self, main_pos, target_pos):
        self.main_pos = main_pos
        self.target_pos = target_pos

