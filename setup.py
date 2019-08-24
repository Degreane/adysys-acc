from setuptools import setup
setup(
    name="AdySys Acc",
    version="0.1",
    url="https://github.com/Degreane/adysys-acc",
    author="Faysal Al-Banna",
    author_email="degreane@gmail.com",
    description="GiaCom AdySys Accounting System (ISP Billing Interface)",
    requires=[
        'sanic',
        'sanic_session',
        'lxml',
        'pyquery',
        'pymitter',
        'gunicorn',
        'sip',
        'sysrsync',
        'sqlalchemy',
        'mongoengine',
        'tinydb'
    ],
    provides=['adysys_acc'],
    zip_safe=False,
)
