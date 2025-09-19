class Event:
    '''
    所有自定义事件类的基类
    '''
    def __init__(self):
        self.name = "BaseEvent"
        self.flag = 0
        self.data = ''

    #使用魔法方法重载实例的值为事件flag方便调用
    def __int__(self):
        self.slot()
        return self.flag
    def slot(self):
        '''
        在此写检测事件是否发生的逻辑
        '''
        pass

