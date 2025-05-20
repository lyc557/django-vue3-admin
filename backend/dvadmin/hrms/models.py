from django.db import models
from dvadmin.utils.models import CoreModel, table_prefix


class Employee(CoreModel):
    """员工信息表"""
    name = models.CharField(max_length=50, verbose_name="姓名", help_text="姓名")
    employee_id = models.CharField(max_length=50, unique=True, verbose_name="工号", help_text="工号")
    GENDER_CHOICES = (
        (0, "未知"),
        (1, "男"),
        (2, "女"),
    )
    gender = models.IntegerField(
        choices=GENDER_CHOICES, default=0, verbose_name="性别", null=True, blank=True, help_text="性别"
    )
    phone = models.CharField(max_length=20, verbose_name="联系电话", null=True, blank=True, help_text="联系电话")
    email = models.EmailField(max_length=50, verbose_name="邮箱", null=True, blank=True, help_text="邮箱")
    address = models.CharField(max_length=200, verbose_name="住址", null=True, blank=True, help_text="住址")
    birth_date = models.DateField(verbose_name="出生日期", null=True, blank=True, help_text="出生日期")
    hire_date = models.DateField(verbose_name="入职日期", null=True, blank=True, help_text="入职日期")
    dept = models.ForeignKey(
        to="system.Dept",
        verbose_name="所属部门",
        on_delete=models.PROTECT,
        db_constraint=False,
        null=True,
        blank=True,
        help_text="所属部门",
    )
    position = models.ForeignKey(
        to="Position",
        verbose_name="职位",
        on_delete=models.PROTECT,
        db_constraint=False,
        null=True,
        blank=True,
        help_text="职位",
    )
    EMPLOYEE_STATUS = (
        (0, "在职"),
        (1, "离职"),
        (2, "试用期"),
    )
    status = models.IntegerField(
        choices=EMPLOYEE_STATUS, default=0, verbose_name="员工状态", help_text="员工状态"
    )
    
    class Meta:
        db_table = table_prefix + "hrms_employee"
        verbose_name = "员工信息表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)


class Position(CoreModel):
    """职位表"""
    name = models.CharField(max_length=50, verbose_name="职位名称", help_text="职位名称")
    code = models.CharField(max_length=50, unique=True, verbose_name="职位编码", help_text="职位编码")
    description = models.TextField(verbose_name="职位描述", null=True, blank=True, help_text="职位描述")
    
    class Meta:
        db_table = table_prefix + "hrms_position"
        verbose_name = "职位表"
        verbose_name_plural = verbose_name
        ordering = ("code",)


class Attendance(CoreModel):
    """考勤记录表"""
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
    ATTENDANCE_STATUS = (
        (0, "正常"),
        (1, "迟到"),
        (2, "早退"),
        (3, "旷工"),
        (4, "请假"),
    )
    status = models.IntegerField(
        choices=ATTENDANCE_STATUS, default=0, verbose_name="考勤状态", help_text="考勤状态"
    )
    remark = models.TextField(verbose_name="备注", null=True, blank=True, help_text="备注")
    
    class Meta:
        db_table = table_prefix + "hrms_attendance"
        verbose_name = "考勤记录表"
        verbose_name_plural = verbose_name
        ordering = ("-date",)
        unique_together = ("employee", "date")


class Leave(CoreModel):
    """请假记录表"""
    employee = models.ForeignKey(
        to="Employee",
        verbose_name="员工",
        on_delete=models.CASCADE,
        db_constraint=False,
        help_text="员工",
    )
    LEAVE_TYPE = (
        (0, "事假"),
        (1, "病假"),
        (2, "年假"),
        (3, "调休"),
        (4, "婚假"),
        (5, "产假"),
        (6, "丧假"),
        (7, "其他"),
    )
    leave_type = models.IntegerField(
        choices=LEAVE_TYPE, default=0, verbose_name="请假类型", help_text="请假类型"
    )
    start_date = models.DateTimeField(verbose_name="开始时间", help_text="开始时间")
    end_date = models.DateTimeField(verbose_name="结束时间", help_text="结束时间")
    days = models.FloatField(verbose_name="请假天数", help_text="请假天数")
    reason = models.TextField(verbose_name="请假原因", help_text="请假原因")
    APPROVAL_STATUS = (
        (0, "待审批"),
        (1, "已批准"),
        (2, "已拒绝"),
    )
    status = models.IntegerField(
        choices=APPROVAL_STATUS, default=0, verbose_name="审批状态", help_text="审批状态"
    )
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
    approval_time = models.DateTimeField(verbose_name="审批时间", null=True, blank=True, help_text="审批时间")
    approval_remark = models.TextField(verbose_name="审批备注", null=True, blank=True, help_text="审批备注")
    
    class Meta:
        db_table = table_prefix + "hrms_leave"
        verbose_name = "请假记录表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)


class Resume(CoreModel):
    """简历模型"""
    file = models.FileField(upload_to='resume/%Y/%m/%d/', verbose_name='简历文件')
    file_name = models.CharField(max_length=255, verbose_name='文件名称')
    file_type = models.CharField(max_length=100, verbose_name='文件类型')
    file_size = models.IntegerField(verbose_name='文件大小(KB)')
    content = models.TextField(null=True, blank=True, verbose_name='简历内容')
    analysis_result = models.JSONField(null=True, blank=True, verbose_name='分析结果')
    
    class Meta:
        db_table = table_prefix + "hrms_resume"
        verbose_name = "简历表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)