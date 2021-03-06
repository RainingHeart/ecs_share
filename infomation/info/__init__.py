import logging
from logging.handlers import RotatingFileHandler

from flask_session import Session #只是用来指定session存储数据的位置
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf import CSRFProtect
from config import config_dict
from flask  import Flask

# 创建SQLAlchemy对象
db = SQLAlchemy()

#定义redis
redis_store = None

#抽取工厂方法,根据参数生产不同环境下的app
def create_app(config_name):

    #创建app对象
    app = Flask(__name__)

    #根据config_name获取到配置对象
    config = config_dict.get(config_name)

    #传递日志级别,设置日志信息
    log_file(config.LEVEL)

    #从类中加载配置信息到app
    app.config.from_object(config)

    #使用db,关联app
    db.init_app(app)

    #创建redis对象
    global redis_store
    redis_store = redis.StrictRedis(host=config.REDIS_HOST,port=config.REDIS_PORT,decode_responses=True)

    #设置csrf对app进行保护
    CSRFProtect(app)

    #初始化Session
    Session(app)

    #注册蓝图到app对象
    from info.modules.index import index_blue
    app.register_blueprint(index_blue)

    return app

#配置日志记录信息,就是为了方便记录程序运行过程
def log_file(LEVEL):
    # 设置日志的记录等级,大小关系: DEBUG<INFO<WARING<ERROR
    logging.basicConfig(level=LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)