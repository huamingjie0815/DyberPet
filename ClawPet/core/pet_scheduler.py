import sys
import time
from datetime import datetime, timedelta

from apscheduler.schedulers.qt import QtScheduler
from apscheduler.triggers import interval, date, cron

from PySide6.QtCore import QObject, Signal

import ClawPet.settings as settings
basedir = settings.BASEDIR


##############################
#          计划任务
##############################
class Scheduler_worker(QObject):
    sig_settext_sche = Signal(str, str, name='sig_settext_sche')
    sig_setact_sche = Signal(str, name='sig_setact_sche')
    sig_focus_end = Signal(name='sig_focus_end')
    sig_tomato_end = Signal(name='sig_tomato_end')
    sig_settime_sche = Signal(str, int, name='sig_settime_sche')
    sig_setup_bubble = Signal(dict, name='sig_setup_bubble')


    def __init__(self, parent=None):
        """
        Scheduler Module
        Time-related processor

        """
        super(Scheduler_worker, self).__init__(parent)
        #self.pet_conf = pet_conf
        self.is_killed = False
        self.is_paused = False
        #self.activated_times = 0
        self.new_task = False
        self.task_name = None
        self.n_tomato = None
        self.n_tomato_now = None
        self.focus_on = False
        self.tomato_list = []
        self.focus_time = 0
        self.tm_interval = 25
        self.tm_break = 5

        ''' Customized Pomodoro function deleted from v0.3.7
        pomodoro_conf = os.path.join(basedir, 'res/icons/Pomodoro.json')
        if os.path.isfile(pomodoro_conf):
            self.tm_config = json.load(open(pomodoro_conf, 'r', encoding='UTF-8'))
        else:
            self.tm_config = {"title":"番茄钟",
                        "Description": "番茄工作法是一种时间管理方法，该方法使用一个定时器来分割出25分钟的工作时间和5分钟的休息时间，提高效率。",
                        "option_text": "想要执行",
                        "options":{"pomodoro": {
                                             "note_start":"新的番茄时钟开始了哦！加油！",
                                             "note_first":"个番茄时钟设定完毕！开始了哦！",
                                             "note_end":"叮叮~ 番茄时间到啦！休息5分钟！",
                                             "note_last":"叮叮~ 番茄时间全部结束啦！"
                                             }
                                  }
                        }
        '''
        self.pomodoro_text = {"name": self.tr("Pomodoro"),
                              "note_start": self.tr("The new Pomodoro has started! Let's go!"),
                              "note_first": self.tr(" Pomodoros have been set! Let's dive in!"),
                              "note_end": self.tr("Ding ding~ Pomodoro finished! Time for a 5-minute break!"),
                              "note_last": self.tr("Ding ding~ All Pomodoros completed! Great job!"),
                              "note_cancel": self.tr("Your Pomodoros have all been canceled!")}

        self.focus_text = {"name": self.tr("Focus Session"),
                           "note_start": self.tr("Your focus session has started!"),
                           "note_end": self.tr("Your focus session has completed!"),
                           "note_cancel": self.tr("Your focus session has been canceled!")}

        self.scheduler = QtScheduler()
        self.scheduler.start()


    def run(self):
        """Run Scheduler in a separate thread"""
        #time.sleep(10)
        now_time = datetime.now().hour
        greet_type, greet_text = self.greeting(now_time)
        #comp_days = '这是陪伴你的第 %i 天 <3'%(settings.pet_data.days)
        if not settings.settingGood:
            settingBrokeNote = self.tr("*Setting config file broken. Setting is re-initialized.")
            self.show_dialogue('system', settingBrokeNote)
        else:
            settingBrokeNote = ""
        if not settings.pet_data.saveGood:
            saveBrokeNote = self.tr("*Game save file broken. Data is re-initialized.\nPlease load previous saved data to recover.")
            self.show_dialogue('system', saveBrokeNote)
        else:
            saveBrokeNote = ""
        #self.show_dialogue(greet_type, f'{greet_text}')
        self.sig_setup_bubble.emit({'message':greet_text, 'start_audio':greet_type, 'icon':None})


    def kill(self):
        self.is_paused = False
        self.is_killed = True
        self.scheduler.shutdown()


    def pause(self):
        self.is_paused = True
        self.scheduler.pause()


    def resume(self):
        self.is_paused = False
        self.scheduler.resume()

    def send_greeting(self):
        now_time = datetime.now().hour
        greet_type, greet_text = self.greeting(now_time)
        #comp_days = '这是陪伴你的第 %i 天 <3'%(settings.pet_data.days)
        #self.show_dialogue(greet_type, '%s'%(greet_text))
        self.sig_setup_bubble.emit({'message':greet_text, 'start_audio':greet_type, 'icon':None})


    def greeting(self, time):
        if 11 >= time >= 6:
            return 'greeting_1', self.tr("Good Morning!") #'早上好!'
        elif 13 >= time >= 12:
            return 'greeting_2', self.tr("Good Afternoon!") #'中午好!'
        elif 18 >= time >= 14:
            return 'greeting_3', self.tr("Good Afternoon!") #'下午好！'
        elif 22 >= time >= 19:
            return 'greeting_4', self.tr("Good Evening!") #'晚上好!'
        elif 24 >= time >= 23:
            return 'greeting_5', self.tr("Time to sleep!") #'该睡觉啦!'
        elif 5 >= time >= 0:
            return 'greeting_5', self.tr("Time to sleep!") #'该睡觉啦!'
        else:
            return 'None','None'


    def show_dialogue(self, note_type, texts_toshow):
        # 排队 避免对话显示冲突
        while settings.showing_dialogue_now:
            time.sleep(1)
        settings.showing_dialogue_now = True

        #for text_toshow in texts_toshow:
        self.sig_settext_sche.emit(note_type, texts_toshow) #text_toshow)
        #    time.sleep(3)
        #self.sig_settext_sche.emit('None')
        settings.showing_dialogue_now = False


    def add_tomato(self, n_tomato=None):

        if self.focus_on == False and self.n_tomato_now is None:
            self.n_tomato_now = n_tomato
            time_plus = 0 #25

            # 1-start
            task_text = 'tomato_first'
            time_torun = datetime.now() + timedelta(seconds=1)
            #self.scheduler.add_job(self.run_task, run_date=time_torun, args=[task_text])
            self.scheduler.add_job(self.run_tomato, date.DateTrigger(run_date=time_torun), args=[task_text])

            time_plus += self.tm_interval #25
            #1-end
            if n_tomato == 1:
                task_text = 'tomato_last'
            else:
                task_text = 'tomato_end'
            time_torun = datetime.now() + timedelta(minutes=time_plus) #minutes=time_plus)
            #self.scheduler.add_job(self.run_task, run_date=time_torun, args=[task_text])
            self.scheduler.add_job(self.run_tomato, date.DateTrigger(run_date=time_torun), args=[task_text], id='tomato_0_end')
            self.tomato_list.append('tomato_0_end')
            time_plus += self.tm_break #5

            # others start and end
            if n_tomato > 1:
                for i in range(1, n_tomato):
                    #start
                    task_text = 'tomato_start'
                    time_torun = datetime.now() + timedelta(minutes=time_plus) #minutes=time_plus)
                    #self.scheduler.add_job(self.run_task, run_date=time_torun, args=[task_text])
                    self.scheduler.add_job(self.run_tomato, date.DateTrigger(run_date=time_torun), args=[task_text], id='tomato_%s_start'%i)
                    time_plus += self.tm_interval #25
                    #end
                    if i == (n_tomato-1):
                        task_text = 'tomato_last'
                    else:
                        task_text = 'tomato_end'
                    time_torun = datetime.now() + timedelta(minutes=time_plus) #minutes=time_plus)
                    #self.scheduler.add_job(self.run_task, run_date=time_torun, args=[task_text])
                    self.scheduler.add_job(self.run_tomato, date.DateTrigger(run_date=time_torun), args=[task_text], id='tomato_%s_end'%i)
                    time_plus += self.tm_break #5
                    self.tomato_list.append('tomato_%s_start'%i)
                    self.tomato_list.append('tomato_%s_end'%i)

        ''' From v0.3.7, situations below won't happen
        elif self.focus_on:
            task_text = "focus_on"
            time_torun = datetime.now() + timedelta(seconds=1)
            self.scheduler.add_job(self.run_tomato, date.DateTrigger(run_date=time_torun), args=[task_text])
        else:
            task_text = "tomato_exist"
            time_torun = datetime.now() + timedelta(seconds=1)
            #self.scheduler.add_job(self.run_task, run_date=time_torun, args=[task_text])
            self.scheduler.add_job(self.run_tomato, date.DateTrigger(run_date=time_torun), args=[task_text])
        '''



    def run_tomato(self, task_text):
        text_toshow = ''
        #finished = False

        if task_text == 'tomato_start':
            self.tomato_timeleft = self.tm_interval #25
            self.scheduler.add_job(self.change_tomato, interval.IntervalTrigger(minutes=1), id='tomato_timer', replace_existing=True)
            self.sig_settime_sche.emit('tomato_start', self.tomato_timeleft)
            self.tomato_list = self.tomato_list[1:]
            text_toshow = self.pomodoro_text['note_start']

        elif task_text == 'tomato_first':
            self.scheduler.add_job(self.change_tomato, interval.IntervalTrigger(minutes=1), id='tomato_timer', replace_existing=True)
            self.tomato_timeleft = self.tm_interval #25
            self.sig_settime_sche.emit('tomato_start', self.tomato_timeleft)
            text_toshow = "%s%s"%(int(self.n_tomato_now), self.pomodoro_text['note_first'])

        elif task_text == 'tomato_end':
            self.tomato_timeleft = self.tm_break #5
            self.scheduler.add_job(self.change_tomato, interval.IntervalTrigger(minutes=1), id='tomato_timer', replace_existing=True)
            self.sig_settime_sche.emit('tomato_rest', self.tomato_timeleft)
            self.tomato_list = self.tomato_list[1:]
            text_toshow = self.pomodoro_text['note_end'] #'叮叮~ 番茄时间到啦！休息5分钟！'
            #finished = True

        elif task_text == 'tomato_last':
            try:
                self.scheduler.remove_job('tomato_timer')
            except:
                pass
            self.tomato_timeleft = 0
            self.n_tomato_now=None
            self.tomato_list = []
            self.sig_tomato_end.emit()
            self.sig_settime_sche.emit('tomato_end', self.tomato_timeleft)
            text_toshow = self.pomodoro_text['note_last']
            #finished = True

        elif task_text == 'tomato_cancel':
            self.n_tomato_now=None
            for iidd in self.tomato_list:
                self.scheduler.remove_job(iidd)
            self.tomato_list = []
            try:
                self.scheduler.remove_job('tomato_timer')
            except:
                pass
            self.tomato_timeleft = 0
            self.sig_settime_sche.emit('tomato_cencel', self.tomato_timeleft)
            self.sig_tomato_end.emit()
            text_toshow = self.pomodoro_text['note_cancel']

        ''' Theoretically, such situation won't exist from v0.3.7 on.
        elif task_text == 'tomato_exist':
            self.sig_tomato_end.emit()
            self.sig_settime_sche.emit('tomato_end', 0)
            text_toshow = "不行！还有 [%s] 在进行哦~"%(settings.current_tm_option)

        elif task_text == 'focus_on':
            self.sig_tomato_end.emit()
            self.sig_settime_sche.emit('tomato_end', 0)
            text_toshow = "不行！还有专注任务在进行哦~"
        '''
        if text_toshow:
            if task_text in ['tomato_start', 'tomato_first']:
                self.show_dialogue('start_tomato', text_toshow)

            elif task_text in ['tomato_end', 'tomato_last']:
                self.show_dialogue('end_tomato', text_toshow)

            elif task_text == 'tomato_cancel':
                self.show_dialogue('cancel_tomato', text_toshow)
        '''
        if finished:
            time.sleep(1)
            self.item_drop(n_minutes=30)
        '''
        #else:
        #    text_toshow = '叮叮~ 你的任务 [%s] 到时间啦！'%(task_text)

    def cancel_tomato(self):
        task_text = "tomato_cancel"
        time_torun_2 = datetime.now() + timedelta(seconds=1)
        self.scheduler.add_job(self.run_tomato, date.DateTrigger(run_date=time_torun_2), args=[task_text])

    def change_tomato(self):
        self.tomato_timeleft += -1
        if self.tomato_timeleft <= 1:
            self.scheduler.remove_job('tomato_timer')
        self.sig_settime_sche.emit('tomato', self.tomato_timeleft)

    def change_focus(self):
        self.focus_time += -1
        if self.focus_time <= 1:
            self.scheduler.remove_job('focus_timer')
        self.sig_settime_sche.emit('focus', self.focus_time)


    def add_focus(self, time_range=None, time_point=None):
        ''' From v0.3.7, situations below won't happen
        if self.n_tomato_now is not None:
            task_text = "tomato_exist"
            time_torun = datetime.now() + timedelta(seconds=1)
            self.scheduler.add_job(self.run_focus, date.DateTrigger(run_date=time_torun), args=[task_text])

        elif self.focus_on:
            task_text = "focus_exist"
            time_torun = datetime.now() + timedelta(seconds=1)
            self.scheduler.add_job(self.run_focus, date.DateTrigger(run_date=time_torun), args=[task_text])
        '''

        if time_range is not None:
            if sum(time_range) == 0:
                return
            else:
                self.focus_on = True
                task_text = "focus_start"
                time_torun = datetime.now() + timedelta(seconds=1)
                self.focus_time = int(time_range[0]*60 + time_range[1])
                self.scheduler.add_job(self.run_focus, date.DateTrigger(run_date=time_torun), args=[task_text])

                task_text = "focus_end"
                time_torun = datetime.now() + timedelta(hours=time_range[0], minutes=time_range[1])
                self.scheduler.add_job(self.run_focus, date.DateTrigger(run_date=time_torun), args=[task_text,self.focus_time], id='focus')

        ''' From v0.3.7, setting up by time_point has been deleted from UI
        elif time_point is not None:
            now = datetime.now()
            time_torun = datetime(year=now.year, month=now.month, day=now.day,
                                  hour=time_point[0], minute=time_point[1], second=0) #now.second)
            time_diff = time_torun - now
            self.focus_time = time_diff.total_seconds() // 60

            if time_diff <= timedelta(0):
                time_torun = time_torun + timedelta(days=1)
                self.focus_time += 24*60

                self.focus_on = True
                task_text = "focus_start_tomorrow"
                time_torun_2 = datetime.now() + timedelta(seconds=1)
                self.scheduler.add_job(self.run_focus, date.DateTrigger(run_date=time_torun_2), args=[task_text])

                task_text = "focus_end"
                self.scheduler.add_job(self.run_focus, date.DateTrigger(run_date=time_torun), args=[task_text,self.focus_time], id='focus')
            else:
                self.focus_on = True
                task_text = "focus_start"
                time_torun_2 = datetime.now() + timedelta(seconds=1)
                self.scheduler.add_job(self.run_focus, date.DateTrigger(run_date=time_torun_2), args=[task_text])

                task_text = "focus_end"
                self.scheduler.add_job(self.run_focus, date.DateTrigger(run_date=time_torun), args=[task_text,self.focus_time], id='focus')
        '''

    def run_focus(self, task_text, n_minutes=0):
        text_toshow = ''
        #finished = False
        ''' From v0.3.7, situations below won't happen
        if task_text == 'tomato_exist':
            self.sig_focus_end.emit()
            self.sig_settime_sche.emit('focus_end', 0)
            text_toshow = '不行！还有 [%s] 在进行哦~'%(settings.current_tm_option)

        elif task_text == 'focus_exist':
            self.sig_focus_end.emit()
            self.sig_settime_sche.emit('focus_end', 0)
            text_toshow = "不行！还有专注任务在进行哦~"
        '''
        if task_text == 'focus_start':
            if self.focus_time > 1:
                self.scheduler.add_job(self.change_focus, interval.IntervalTrigger(minutes=1), id='focus_timer', replace_existing=True)
            #elif self.focus_time < 1:
                #focus_time_sec = int()
            self.sig_settime_sche.emit('focus_start', self.focus_time)
            text_toshow = self.focus_text['note_start'] #"你的专注任务开始啦！"


        elif task_text == 'focus_end':
            self.focus_time = 0
            try:
                self.scheduler.remove_job('focus_timer')
            except:
                pass
            self.sig_settime_sche.emit('focus_end', self.focus_time)
            self.focus_on = False
            self.sig_focus_end.emit()
            text_toshow = self.focus_text['note_end'] #"你的专注任务结束啦！"
            #finished = True


        elif task_text == 'focus_cancel':
            self.focus_time = 0
            try:
                self.scheduler.remove_job('focus_timer')
            except:
                pass
            self.sig_settime_sche.emit('focus_cancel', self.focus_time)
            self.sig_focus_end.emit()
            self.focus_on = False
            text_toshow = self.focus_text['note_cancel'] #"你的专注任务取消啦！"
            #finished = True

        if text_toshow:
            if task_text == 'focus_start':
                self.show_dialogue('start_focus', text_toshow)

            elif task_text == 'focus_end':
                self.show_dialogue('end_focus', text_toshow)

            elif task_text == 'focus_cancel':
                self.show_dialogue('cancel_focus', text_toshow)

        ''' From v0.3.7, situations below won't happen
        elif task_text == 'focus_start_tomorrow':
            if self.focus_time > 1:
                self.scheduler.add_job(self.change_focus, interval.IntervalTrigger(minutes=1), id='focus_timer', replace_existing=True)
            self.sig_settime_sche.emit('focus_start', self.focus_time)
            text_toshow = "专注任务开始啦！\n但设定在明天，请确认无误哦~"

        elif task_text == 'focus_pause':
            try:
                self.scheduler.remove_job('focus_timer')
            except:
                pass
            #self.sig_settime_sche.emit('focus_end', self.focus_time)
            #self.sig_focus_end.emit()
            #self.focus_on = False
            text_toshow = "你的专注任务暂停啦！"

        elif task_text == 'focus_resume':
            if self.focus_time > 1:
                self.scheduler.add_job(self.change_focus, interval.IntervalTrigger(minutes=1), id='focus_timer', replace_existing=True)

            self.sig_settime_sche.emit('focus', self.focus_time)
            text_toshow = "你的专注任务继续进行啦！"
        '''

    ''' Pause function deleted from v0.3.7
    def pause_focus(self):
        try:
            self.scheduler.remove_job('focus')
        except:
            pass
        task_text = "focus_pause"
        time_torun_2 = datetime.now() + timedelta(seconds=1)
        self.scheduler.add_job(self.run_focus, date.DateTrigger(run_date=time_torun_2), args=[task_text])

    def resume_focus(self, remains, total):
        task_text = "focus_resume"
        self.focus_time = remains
        time_torun = datetime.now() + timedelta(seconds=1)
        self.scheduler.add_job(self.run_focus, date.DateTrigger(run_date=time_torun), args=[task_text])

        task_text = "focus_end"
        time_torun = datetime.now() + timedelta(minutes=remains)
        self.scheduler.add_job(self.run_focus, date.DateTrigger(run_date=time_torun), args=[task_text,total], id='focus')
    '''
    def cancel_focus(self, time_past):
        try:
            self.scheduler.remove_job('focus')
        except:
            pass
        task_text = "focus_cancel"
        time_torun_2 = datetime.now() + timedelta(seconds=1)
        self.scheduler.add_job(self.run_focus, date.DateTrigger(run_date=time_torun_2), args=[task_text,time_past])

    ''' Reminder function deleted from v0.3.7
    def add_remind(self, texts, time_range=None, time_point=None, repeat=False):
        if time_point is not None:
            if repeat:
                certain_minute = int(time_point[1])
                self.scheduler.add_job(self.run_remind,
                                       cron.CronTrigger(minute=certain_minute),
                                       args=[texts])
            else:
                certain_day = datetime.now().day
                certain_hour = int(time_point[0])
                certain_minute = int(time_point[1])
                if certain_hour < datetime.now().hour:
                    certain_day = (datetime.now() + timedelta(days=1)).day
                self.scheduler.add_job(self.run_remind,
                                       cron.CronTrigger(day=certain_day,
                                                        hour=certain_hour,
                                                        minute=certain_minute),
                                       args=[texts])

        elif time_range is not None:
            if repeat:
                interval_minute = int(time_range[1])
                self.scheduler.add_job(self.run_remind,
                                       interval.IntervalTrigger(minutes=interval_minute),
                                       args=[texts])
            else:
                if sum(time_range) == 0:
                    return
                else:
                    time_torun = datetime.now() + timedelta(hours=time_range[0], minutes=time_range[1])
                    self.scheduler.add_job(self.run_remind,
                                           date.DateTrigger(run_date=time_torun),
                                           args=[texts])

        time_torun_2 = datetime.now() + timedelta(seconds=1)
        self.scheduler.add_job(self.run_remind,
                               date.DateTrigger(run_date=time_torun_2),
                               args=['remind_start'])

    def run_remind(self, task_text):
        if task_text == 'remind_start':
            text_toshow = "提醒事项设定完成！"
        else:
            text_toshow = '叮叮~ 时间到啦\n[ %s ]'%task_text

        self.show_dialogue('clock_remind',text_toshow)
    '''

