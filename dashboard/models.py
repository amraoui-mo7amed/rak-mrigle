from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal, InvalidOperation

userModel = get_user_model()


class Notification(models.Model):
    """Notification model for user notifications"""

    class NotificationType(models.TextChoices):
        INFO = "info", _("معلومة")
        SUCCESS = "success", _("نجاح")
        WARNING = "warning", _("تحذير")
        ERROR = "error", _("خطأ")

    user = models.ForeignKey(
        userModel,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("المستخدم"),
    )
    title = models.CharField(max_length=255, verbose_name=_("العنوان"))
    message = models.TextField(verbose_name=_("الرسالة"))
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.INFO,
        verbose_name=_("نوع الإشعار"),
    )
    is_read = models.BooleanField(default=False, verbose_name=_("مقروء"))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاريخ الإنشاء")
    )
    read_at = models.DateTimeField(
        blank=True, null=True, verbose_name=_("تاريخ القراءة")
    )
    link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("الرابط"),
        help_text=_("رابط اختياري للتنقل"),
    )

    class Meta:
        verbose_name = _("إشعار")
        verbose_name_plural = "الإشعارات"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class Category(models.Model):
    """Category for transport and machinery services"""

    class CategoryType(models.TextChoices):
        TRANSPORT = "transport", _("Transport")
        MACHINERY = "machinery", _("Machinery")
        LOGISTICS = "logistics", _("Logistics")

    name_ar = models.CharField(max_length=100, verbose_name=_("الاسم بالعربية"))
    name_fr = models.CharField(max_length=100, verbose_name=_("الاسم بالفرنسية"))
    name_en = models.CharField(max_length=100, verbose_name=_("الاسم بالإنجليزية"))
    category_type = models.CharField(
        max_length=20,
        choices=CategoryType.choices,
        verbose_name=_("نوع الفئة"),
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("الأيقونة"),
        help_text=_("FontAwesome icon class"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاريخ الإنشاء")
    )

    class Meta:
        verbose_name = _("فئة")
        verbose_name_plural = "الفئات"
        ordering = ["category_type", "name_ar"]

    def __str__(self):
        return self.name_ar

    def get_name(self, lang="ar"):
        if lang == "fr":
            return self.name_fr
        elif lang == "en":
            return self.name_en
        return self.name_ar


class Offer(models.Model):
    """Offer model for provider service offerings"""

    class OfferStatus(models.TextChoices):
        DRAFT = "draft", _("مسودة")
        PENDING = "pending", _("في الانتظار")
        ACTIVE = "active", _("نشط")
        REJECTED = "rejected", _("مرفوض")
        EXPIRED = "expired", _("منتهي")

    class PricingType(models.TextChoices):
        DISTANCE = "distance", _("مسافة")
        HOURLY = "hourly", _("ساعي")

    provider = models.ForeignKey(
        userModel,
        on_delete=models.CASCADE,
        related_name="offers",
        verbose_name=_("المزود"),
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="offers",
        verbose_name=_("الفئة"),
    )
    title_ar = models.CharField(max_length=200, verbose_name=_("العنوان بالعربية"))
    title_fr = models.CharField(max_length=200, verbose_name=_("العنوان بالفرنسية"))
    title_en = models.CharField(max_length=200, verbose_name=_("العنوان بالإنجليزية"))
    description_ar = models.TextField(verbose_name=_("الوصف بالعربية"))
    description_fr = models.TextField(verbose_name=_("الوصف بالفرنسية"))
    description_en = models.TextField(verbose_name=_("الوصف بالإنجليزية"))
    pricing_type = models.CharField(
        max_length=20,
        choices=PricingType.choices,
        default=PricingType.DISTANCE,
        verbose_name=_("نوع التسعير"),
    )
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("السعر الأساسي"),
        help_text=_("Minimum charge for the service"),
    )
    price_per_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("السعر لكل كلم"),
    )
    price_per_hour = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("السعر لكل ساعة"),
    )
    fuel_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("تكلفة الوقود"),
    )
    operator_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("تكلفة المشغل"),
    )
    wait_time_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("تكلفة وقت الانتظار"),
    )
    capacity = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("السعة"),
        help_text=_("Load capacity (e.g., '5 tons', '20 m³')"),
    )
    wilaya = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("الولاية"),
    )
    image = models.ImageField(
        upload_to="offers/",
        blank=True,
        null=True,
        verbose_name=_("الصورة"),
    )
    status = models.CharField(
        max_length=20,
        choices=OfferStatus.choices,
        default=OfferStatus.DRAFT,
        verbose_name=_("الحالة"),
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name=_("متاح"),
        help_text=_("Available for booking"),
    )
    location_ar = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("الموقع بالعربية"),
    )
    location_fr = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("الموقع بالفرنسية"),
    )
    location_en = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("الموقع بالإنجليزية"),
    )
    admin_note = models.TextField(
        blank=True,
        verbose_name=_("ملاحظة المدير"),
        help_text=_("Internal note for rejection reason"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاريخ الإنشاء")
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("عرض")
        verbose_name_plural = "العروض"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title_ar

    def get_title(self, lang="ar"):
        if lang == "fr":
            return self.title_fr
        elif lang == "en":
            return self.title_en
        return self.title_ar

    def get_description(self, lang="ar"):
        if lang == "fr":
            return self.description_fr
        elif lang == "en":
            return self.description_en
        return self.description_ar

    def get_location(self, lang="ar"):
        if lang == "fr":
            return self.location_fr
        elif lang == "en":
            return self.location_en
        return self.location_ar

    def save(self, *args, **kwargs):
        decimal_fields = [
            "base_price",
            "price_per_km",
            "price_per_hour",
            "fuel_cost",
            "operator_cost",
            "wait_time_cost",
        ]
        for field in decimal_fields:
            value = getattr(self, field)
            if value is not None:
                try:
                    if not isinstance(value, Decimal):
                        value = Decimal(str(value))
                    quantized = value.quantize(Decimal("0.01"))
                    setattr(self, field, quantized)
                except (InvalidOperation, ValueError) as e:
                    raise ValueError(
                        f"Invalid decimal value for {field}: {value}. {str(e)}"
                    )
        super().save(*args, **kwargs)


class ServiceRequest(models.Model):
    """Service request from customer to provider"""

    class RequestStatus(models.TextChoices):
        PENDING = "pending", _("قيد الانتظار")
        APPROVED = "approved", _("مقبول")
        REJECTED = "rejected", _("مرفوض")
        CANCELLED = "cancelled", _("ملغي")

    customer = models.ForeignKey(
        userModel,
        on_delete=models.CASCADE,
        related_name="service_requests",
        verbose_name=_("العميل"),
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name="requests",
        verbose_name=_("العرض"),
    )
    full_name = models.CharField(max_length=200, verbose_name=_("الاسم الكامل"))
    phone = models.CharField(max_length=20, verbose_name=_("رقم الهاتف"))
    wilaya = models.CharField(max_length=100, verbose_name=_("الولاية"))
    location = models.TextField(verbose_name=_("موقع الانطلاق"))
    destination = models.TextField(blank=True, verbose_name=_("الوجهة"))
    notes = models.TextField(blank=True, verbose_name=_("ملاحظات"))
    status = models.CharField(
        max_length=20,
        choices=RequestStatus.choices,
        default=RequestStatus.PENDING,
        verbose_name=_("الحالة"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاريخ الإنشاء")
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("طلب خدمة")
        verbose_name_plural = "طلبات الخدمات"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.offer.title_ar}"


class CommissionBalance(models.Model):
    """Tracks provider's commission balance"""

    provider = models.OneToOneField(
        userModel,
        on_delete=models.CASCADE,
        related_name="commission_balance",
        verbose_name=_("المزود"),
    )
    total_commission = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("إجمالي العمولة"),
    )
    is_blocked = models.BooleanField(
        default=False,
        verbose_name=_("محظور"),
        help_text=_("Offer suspended due to unpaid commission"),
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("رصيد العمولة")
        verbose_name_plural = "أرصدة العمولات"

    def __str__(self):
        return f"{self.provider.username} - {self.total_commission} DA"


class CommissionTransaction(models.Model):
    """Individual commission transaction per approved request"""

    provider = models.ForeignKey(
        userModel,
        on_delete=models.CASCADE,
        related_name="commission_transactions",
        verbose_name=_("المزود"),
    )
    service_request = models.OneToOneField(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="commission_transaction",
        verbose_name=_("طلب الخدمة"),
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name="commission_transactions",
        verbose_name=_("العرض"),
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("المبلغ"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء"),
    )

    class Meta:
        verbose_name = _("معاملة العمولة")
        verbose_name_plural = "معاملات العمولات"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.provider.username} - {self.amount} DA"


class PaymentProof(models.Model):
    """Payment proof submitted by provider"""

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", _("قيد الانتظار")
        APPROVED = "approved", _("مقبول")
        REJECTED = "rejected", _("مرفوض")

    provider = models.ForeignKey(
        userModel,
        on_delete=models.CASCADE,
        related_name="payment_proofs",
        verbose_name=_("المزود"),
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name="payment_proofs",
        verbose_name=_("العرض"),
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("المبلغ"),
    )
    proof_file = models.FileField(
        upload_to="payment_proofs/",
        verbose_name=_("ملف الإثبات"),
        help_text=_("PDF أو صورة فقط"),
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name=_("الحالة"),
    )
    admin_note = models.TextField(
        blank=True,
        verbose_name=_("ملاحظة المدير"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء"),
    )
    reviewed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("تاريخ المراجعة"),
    )

    class Meta:
        verbose_name = _("إثبات الدفع")
        verbose_name_plural = "إثباتات الدفع"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.provider.username} - {self.amount} DA"
