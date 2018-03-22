from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	username = models.CharField(max_length=200, verbose_name=_("username"))
	categories = models.ManyToManyField("Category", blank=True, verbose_name=_("category"))
	completed_tasks = models.IntegerField(null=True, blank=True)
	spent_time = models.IntegerField(null=True, blank=True)
	lazy_days = models.IntegerField(null=True, blank=True)
	created_at = models.DateField(auto_now_add=True)

	def __unicode__(self):
		return self.username

	def __str__(self):
		return self.username

	class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")
        ordering = ["-created_at"]


class Category(models.Model):
	name = models.CharField(max_length=200, verbose_name=_("category name"))
	parent = models.ForeignKey("Category", on_delete=models.CASCADE, blank=True)
	aim = models.TextField(verbose_name=_("what person want to get"), blank=True)
	completed_tasks = models.IntegerField(null=True, blank=True)
	spent_time = models.IntegerField(null=True, blank=True)
	lazy_days = models.IntegerField(null=True, blank=True)
	created_at = models.DateField(auto_now_add=True)

	def __unicode__(self):
		return self.name

	def __str__(self):
		return self.name

	class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ["lazy_days"]


class Programm(models.Model):
	name = models.CharField(max_length=200, verbose_name=_("programm name"))
	category = models.ForeignKey(Category, on_delete=models.CASCADE)
	is_active = models.BinaryField(default=False)
	description = models.TextField(verbose_name=_("what is this programm for"), blank=True)
	completed_tasks = models.IntegerField(null=True, blank=True)
	spent_time = models.IntegerField(null=True, blank=True)
	lazy_days = models.IntegerField(null=True, blank=True)
	created_at = models.DateField(auto_now_add=True)
	

	def __unicode__(self):
		return self.name

	def __str__(self):
		return self.name

	class Meta:
        verbose_name = _("programm")
        verbose_name_plural = _("programms")
        ordering = ["lazy_days"]


class Task(models.Model):
	name = models.CharField(max_length=200, verbose_name=_("task"))
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
	programm = models.ForeignKey(Programm, on_delete=models.CASCADE)
	is_finished = models.BinaryField(default=False)
	created_at = models.DateField(auto_now_add=True)
	plan_date = models.DateField(null=True, blank=True)
	finish_date = models.DateField(null=True, blank=True)
	spent_time = models.IntegerField(null=True, blank=True)
	description = models.TextField(verbose_name=_("what is this task about"), blank=True)


	def __unicode__(self):
		return self.name

	def __str__(self):
		return self.name

	class Meta:
        verbose_name = _("task")
        verbose_name_plural = _("tasks")
        ordering = ["-finish_date"]


class Achievment(models.Model):
	task = models.ForeignKey(Task, on_delete=models.CASCADE)
	upload = models.FileField(upload_to=user_directory_path)
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
	description = models.TextField(blank=True)

	def user_directory_path(instance, filename):
	    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
	    return 'user_{0}/{1}'.format(instance.profile.id, filename)


	class Meta:
        verbose_name = _("achievment")
        verbose_name_plural = _("achievments")


class Transaction(models.Model):
	task = models.ForeignKey(Task, on_delete=models.CASCADE)
	spent_time = models.IntegerField()
	created_at = models.DateField(auto_now_add=True)

	class Meta:
        verbose_name = _("transaction")
        verbose_name_plural = _("transactions")
        ordering = ["-created_at"]
        

