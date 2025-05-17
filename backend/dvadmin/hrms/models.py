from django.db import models
from dvadmin.utils.models import CoreModel, table_prefix


class Employee(CoreModel):
    """
    员工信息表
    """
    employee_id = models.CharField(max_length=32, verbose_name="员工编号", help_text="员工编号")
    name = models.CharField(max_length=64, verbose_name="员工姓名", help_text="员工姓名")
    gender_choices = (
        (0, "未知"),
        (1, "男"),
        (2, "女"),
    )
    gender = models.IntegerField(choices=gender_choices, default=0, verbose_name="性别", help_text="性别")
    phone = models.CharField(max_length=32, verbose_name="联系电话", null=True, blank=True, help_text="联系电话")
    email = models.EmailField(max_length=64, verbose_name="邮箱", null=True, blank=True, help_text="邮箱")
    dept = models.ForeignKey(
        to="system.Dept",
        verbose_name="所属部门",
        on_delete=models.PROTECT,
        db_constraint=False,
        null=True,
        blank=True,
        help_text="所属部门",
    )
    position = models.CharField(max_length=64, verbose_name="职位", null=True, blank=True, help_text="职位")
    hire_date = models.DateField(verbose_name="入职日期", null=True, blank=True, help_text="入职日期")
    status_choices = (
        (0, "离职"),
        (1, "在职"),
        (2, "试用期"),
    )
    status = models.IntegerField(choices=status_choices, default=1, verbose_name="员工状态", help_text="员工状态")

    class Meta:
        db_table = table_prefix + "hrms_employee"
        verbose_name = "员工信息表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)


class Attendance(CoreModel):
    """
    考勤记录表
    """
    employee = models.ForeignKey(
        to="Employee",
        verbose_name="员工",
        on_delete=models.CASCADE,
        db_constraint=False,
        help_text="员工",
    )
    date = models.DateField(verbose_name="日期", help_text="日期")
    check_in = models.DateTimeField(verbose_name="签到时间", null=True, blank=True, help_text="签到时间")
    check_out = models.DateTimeField(verbose_name="签退时间", null=True, blank=True, help_text="签退时间")
    status_choices = (
        (0, "正常"),
        (1, "迟到"),
        (2, "早退"),
        (3, "缺勤"),
        (4, "请假"),
    )
    status = models.IntegerField(choices=status_choices, default=0, verbose_name="考勤状态", help_text="考勤状态")
    remark = models.TextField(verbose_name="备注", null=True, blank=True, help_text="备注")

    class Meta:
        db_table = table_prefix + "hrms_attendance"
        verbose_name = "考勤记录表"
        verbose_name_plural = verbose_name
        ordering = ("-date",)


class Leave(CoreModel):
    """
    请假申请表
    """
    employee = models.ForeignKey(
        to="Employee",
        verbose_name="员工",
        on_delete=models.CASCADE,
        db_constraint=False,
        help_text="员工",
    )
    type_choices = (
        (0, "事假"),
        (1, "病假"),
        (2, "年假"),
        (3, "调休"),
        (4, "婚假"),
        (5, "产假"),
        (6, "丧假"),
        (7, "其他"),
    )
    leave_type = models.IntegerField(choices=type_choices, default=0, verbose_name="请假类型", help_text="请假类型")
    start_date = models.DateTimeField(verbose_name="开始时间", help_text="开始时间")
    end_date = models.DateTimeField(verbose_name="结束时间", help_text="结束时间")
    days = models.FloatField(verbose_name="请假天数", help_text="请假天数")
    reason = models.TextField(verbose_name="请假原因", help_text="请假原因")
    status_choices = (
        (0, "待审批"),
        (1, "已批准"),
        (2, "已拒绝"),
        (3, "已取消"),
    )
    status = models.IntegerField(choices=status_choices, default=0, verbose_name="审批状态", help_text="审批状态")
    approver = models.ForeignKey(
        to="system.Users",
        verbose_name="审批人",
        on_delete=models.SET_NULL,
        db_constraint=False,
        null=True,
        blank=True,
        help_text="审批人",
        related_name="leave_approver",
    )
    approve_time = models.DateTimeField(verbose_name="审批时间", null=True, blank=True, help_text="审批时间")
    approve_remark = models.TextField(verbose_name="审批备注", null=True, blank=True, help_text="审批备注")

    class Meta:
        db_table = table_prefix + "hrms_leave"
        verbose_name = "请假申请表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)

def media_file_name(instance, filename):
    """
    生成上传文件的存储路径
    
    Args:
        instance: 模型实例
        filename: 原始文件名
    
    Returns:
        str: 文件存储路径
    """
    import os
    import time
    from django.utils import timezone
    
    # 获取文件扩展名
    ext = filename.split('.')[-1]
    # 使用时间戳和原始文件名生成新的文件名
    new_filename = f"{int(time.time())}_{filename}"
    # 返回上传路径，按年月日组织
    today = timezone.now().strftime('%Y%m%d')
    return os.path.join('resume', today, new_filename)
    
class ResumeFile(CoreModel):
    """
    简历文件模型
    """
    name = models.CharField(max_length=200, null=True, blank=True, verbose_name="文件名称", help_text="文件名称")
    url = models.FileField(upload_to=media_file_name, null=True, blank=True, verbose_name="文件")
    file_url = models.CharField(max_length=255, blank=True, verbose_name="文件地址", help_text="文件地址")
    engine = models.CharField(max_length=100, default='local', blank=True, verbose_name="存储引擎", help_text="存储引擎")
    mime_type = models.CharField(max_length=100, blank=True, verbose_name="Mime类型", help_text="Mime类型")
    size = models.CharField(max_length=36, blank=True, verbose_name="文件大小", help_text="文件大小")
    md5sum = models.CharField(max_length=36, blank=True, verbose_name="文件md5", help_text="文件md5")
    candidate_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="候选人姓名", help_text="候选人姓名")
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name="应聘职位", help_text="应聘职位")
    status = models.IntegerField(default=0, verbose_name="处理状态", help_text="处理状态", 
                               choices=((0, "未处理"), (1, "已查看"), (2, "已联系"), (3, "已面试"), (4, "已录用"), (5, "已拒绝")))
    
    def save(self, *args, **kwargs):
        if not self.md5sum and self.url:  # 文件是新的
            md5 = hashlib.md5()
            for chunk in self.url.chunks():
                md5.update(chunk)
            self.md5sum = md5.hexdigest()
        if not self.size and self.url:
            self.size = self.url.size
        if not self.file_url and self.url:
            url = media_file_name(self, self.name)
            self.file_url = f'media/{url}'
        super(ResumeFile, self).save(*args, **kwargs)
    

    class Meta:
        db_table = table_prefix + "hrms_resume_file"
        verbose_name = "简历文件管理"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)