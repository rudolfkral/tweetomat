from django.contrib import admin
from tpz_core.models import Party, Hashtag, Idol, Quote, Account_stats, Twitter_account, Youtube_account, Text_template

# Register your models here
admin.site.register(Party)
admin.site.register(Hashtag)
admin.site.register(Idol)
admin.site.register(Quote)
admin.site.register(Account_stats)
admin.site.register(Twitter_account)
admin.site.register(Youtube_account)
admin.site.register(Text_template)


