from django.contrib import admin
from goods.models import *
from django.core.cache import cache


class BaseAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        # 新增或更新表中的书据时调用
        super().save_model(request, obj, form, change)
        from db.tasks import task_generate_static_index
        # 发出任务，让celery 我让可燃重新生成首页静态页
        task_generate_static_index.delay()
        cache.delete('cache_idnex')

    def delete_model(self, request, obj):
        # 删除表中的数据时调用
        from db.tasks import task_generate_static_index

        super().delete_model(request, obj)
        task_generate_static_index.delay()
        cache.delete('cache_idnex')


class GoodsSKUAdmin(BaseAdmin):
    pass


class GoodsTypeAdmin(BaseAdmin):
    pass


class GoodsAdmin(BaseAdmin):
    pass


class IndexTypeGoodBannerAdmin(BaseAdmin):
    pass


class IndexPromotionBannerAdmin(BaseAdmin):
    pass


class IndexGoodBannerAdmin(BaseAdmin):
    pass


admin.site.register(GoodType, GoodsSKUAdmin)
admin.site.register(Goods, GoodsAdmin)
admin.site.register(GoodSKU, GoodsSKUAdmin)
admin.site.register(GoodsImage)
admin.site.register(IndexTypeGoodBanner, IndexTypeGoodBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
admin.site.register(IndexGoodBanner, IndexGoodBannerAdmin)
