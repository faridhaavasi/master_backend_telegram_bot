from celery import Celery

app = Celery('clery', broker='rabbit://', backend='rpc://')