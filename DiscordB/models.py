from django.db import models
from colorfield.fields import ColorField
from django.urls.base import reverse
from simple_history.models import HistoricalRecords

# Create your models here.

class DiscordUser(models.Model):

    user_name = models.CharField(max_length=50)
    user_id = models.DecimalField(max_digits=20, decimal_places=0, unique=True)
    user_photo_url = models.URLField(max_length=200)
    user_guilds = models.ManyToManyField("Guild" ,verbose_name=("Guilds"), blank=True, default='None')
    user_guilds_count = models.IntegerField(default=0)
    user_messages_count = models.IntegerField(default=0)
    user_is_bot = models.BooleanField(default=False)
    user_created_at = models.DateField(null=True)
    user_has_nitro = models.BooleanField(default=False)
    user_banner_url = models.URLField(max_length=200, blank=True)
    user_roles = models.ManyToManyField("Role", default='None', blank=True)
    user_history = HistoricalRecords(cascade_delete_history=True)

    class Meta:
        verbose_name = ("Discord User")
        verbose_name_plural = ("Discord Users")

    def __str__(self):
        return self.user_name

    def save(self, *args, **kwargs):
        self.user_guilds_count = self.user_guilds.all().count()
        self.user_messages_count = Message.objects.filter(message_author=DiscordUser.objects.get(user_id=self.user_id)).count()
        super(DiscordUser, self).save(*args, **kwargs) # Call the "real" save() method.

    def get_absolute_url(self):
        return reverse("user", kwargs={"pk": self.pk})

class GuildChannel(models.Model):

    channel_name = models.CharField(max_length=50, editable=False)
    channel_id = models.DecimalField(max_digits=25, decimal_places=1, unique=True)
    channel_guild = models.ForeignKey("Guild", on_delete=models.CASCADE, verbose_name=("Guilds"))
    channel_category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, default='None')
    channel_text = models.BooleanField(default=False)
    channel_history = HistoricalRecords(cascade_delete_history=True)

    class Meta:
        verbose_name = ("Guild Channel")
        verbose_name_plural = ("Guilds Channel")

    def __str__(self):
        return self.channel_name

    def get_absolute_url(self):
        return reverse("GuildChannel_detail", kwargs={"pk": self.pk})

class Guild(models.Model):

    guild_name = models.CharField(max_length=120, verbose_name='Name of guild')
    guild_id = models.DecimalField(max_digits=20, decimal_places=0, unique=True, verbose_name='Server ID') # Technical field
    guild_description = models.TextField(blank=True, default='None', verbose_name='Server description', null=True)
    guild_members = models.IntegerField(default=0)
    guild_channels = models.IntegerField(default=0)
    guild_categoriest = models.IntegerField(default=0)
    guild_roles = models.IntegerField(default=0)
    guild_owner = models.ForeignKey(DiscordUser, on_delete=models.CASCADE, default=None, blank=True, null=True)
    guild_region = models.CharField(max_length=40, default='None')
    guild_default_role = models.ForeignKey('Role', default=1, on_delete=models.CASCADE)
    guild_large = models.BooleanField(default=False)
    guild_verification_level = models.IntegerField(default=0)
    guild_mfa_level = models.IntegerField(default=0)
    guild_created_at = models.DateField(blank=True, default=0)
    guild_photo_url = models.URLField(max_length=200)
    guild_banner_url = models.URLField(max_length=200, blank=True)
    guild_history = HistoricalRecords(cascade_delete_history=True)
    guild_messages = models.IntegerField(verbose_name="Messaages amount", default=0)

    class Meta:
        verbose_name = ("Guild")
        verbose_name_plural = ("Guilds")

    def __str__(self):
        return self.guild_name

    def save(self, *args, **kwargs):
        self.guild_messages = Message.objects.filter(message_guild=Guild.objects.get(guild_id=self.guild_id)).count()
        super(Guild, self).save(*args, **kwargs) # Call the "real" save() method.

    def get_absolute_url(self):
        return reverse("guild", kwargs={"pk": self.pk})

class Category(models.Model):

    category_name = models.CharField(max_length=50, verbose_name='Category')
    category_id = models.DecimalField(max_digits=20, decimal_places=0, unique=True, verbose_name="Category ID", null=True)
    category_guild = models.ForeignKey(Guild, verbose_name='Category', null=True, on_delete=models.CASCADE, blank=True)
    category_history = HistoricalRecords(cascade_delete_history=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.category_name

    def get_absolute_url(self):
        return reverse("сategory", kwargs={"category_id": self.pk})

class Role(models.Model):

    role_name = models.CharField(verbose_name='Role', max_length=120)
    role_is_default = models.BooleanField(default=False)
    role_id = models.DecimalField(max_digits=20, decimal_places=0, unique=True, verbose_name='Role ID', null=True)
    role_guild = models.ManyToManyField(Guild, default='None', blank=True)
    role_color = ColorField(default='#000000')
    role_history = HistoricalRecords(cascade_delete_history=True)

    class Meta:
        verbose_name = ("role")
        verbose_name_plural = ("roles")

    def __str__(self):
        return self.role_name

    def get_absolute_url(self):
        return reverse("role_detail", kwargs={"pk": self.pk})

class Message(models.Model):

    message_content = models.TextField(verbose_name='Content')
    message_author = models.ForeignKey(DiscordUser, on_delete=models.CASCADE, blank=True)
    message_id = models.DecimalField(max_digits=30, decimal_places=0, unique=True, verbose_name='Message ID', null=True, editable=False)
    message_channel = models.ForeignKey(GuildChannel, on_delete=models.CASCADE, blank=True, default="None")
    message_category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, default="None")
    message_guild = models.ForeignKey(Guild, on_delete=models.CASCADE, blank=True, default="None")
    message_pinned = models.BooleanField(default=False)
    message_jump_url = models.URLField(editable=False)
    message_date = models.DateTimeField(auto_now_add=True, editable=False)
    role_history = HistoricalRecords(cascade_delete_history=True)

    class Meta:
        verbose_name = ("Message")
        verbose_name_plural = ("Messages")

    def __str__(self):
        cont = f"Message\nAuthor: {self.message_author}\nGuild: {self.message_guild}\nContent: {self.message_content}"
        return cont

class Emojis(models.Model):

    emoji_name = models.CharField(max_length=255)
    emoji_photo = models.URLField(editable=False)
    emoji_animated = models.BooleanField(default=False)
    emoji_guild = models.ForeignKey(Guild, on_delete=models.CASCADE, default=None, blank=True)
    emoji_id = models.DecimalField(max_digits=30, decimal_places=0, unique=True, verbose_name='Emoji ID', null=True, editable=False)
    role_history = HistoricalRecords(cascade_delete_history=True)

    class Meta:
        verbose_name = ("Emoji")
        verbose_name_plural = ("Emojies")

    def __str__(self):
        return self.emoji_name

class Polls_option(models.Model):

    option_name = models.CharField(max_length=255)
    option_guild = models.ForeignKey(Guild, on_delete=models.CASCADE, blank=True)
    option_voters = models.ManyToManyField(DiscordUser, default='None', blank=True)
    option_poll = models.ForeignKey('Polls', on_delete=models.CASCADE, blank=True, default=0)

    def __str__(self):
        return self.option_name 

class Polls(models.Model):

    polls_id = models.DecimalField(max_digits=30, decimal_places=0, unique=True, verbose_name='Poll ID', null=True, editable=False)
    polls_name = models.CharField(max_length=255)
    polls_author = models.ForeignKey(DiscordUser, on_delete=models.CASCADE, blank=True)
    polls_options = models.ManyToManyField(Polls_option, related_name='options_available',default='None', blank=True)
    polls_time = models.DateTimeField()
    polls_guild = models.ForeignKey(Guild, on_delete=models.CASCADE, blank=True)
    poll_winner = models.ForeignKey(Polls_option, related_name='options_winner', on_delete=models.CASCADE, blank=True, null=True)
    poll_history = HistoricalRecords()

    class Meta:
        verbose_name = ("polls")
        verbose_name_plural = ("pollss")

    def __str__(self):
        return self.polls_name

    def get_absolute_url(self):
        return reverse("polls", kwargs={"pk": self.pk})

