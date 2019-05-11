from crontab import CronTab

my_cron = CronTab(user='isaiahngaruiya')


job = my_cron.new(command='python manage.py send_reminder')

job.hour.every(1)

my_cron.write()
