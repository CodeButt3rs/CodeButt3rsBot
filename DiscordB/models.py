from django.db import models
from colorfield.fields import ColorField
from django.urls.base import reverse
from django.utils import timezone
from simple_history.models import HistoricalRecords

# Create your models here.

class DiscordUser(models.Model):

    user_name = models.CharField(max_length=50, verbose_name='User Name')
    user_id = models.DecimalField(max_digits=20, decimal_places=0, unique=True, verbose_name='User ID')
    user_photo_url = models.URLField(max_length=200)
    user_guilds = models.ManyToManyField("Guild" ,verbose_name=("Guilds"), blank=True, default='None')
    user_guilds_count = models.IntegerField(default=0, verbose_name='User Guilds')
    user_messages_count = models.IntegerField(default=0, verbose_name='User messages')
    user_is_bot = models.BooleanField(default=False, verbose_name='Is bot?')
    user_created_at = models.DateField(null=True, verbose_name='Created at')
    user_has_nitro = models.BooleanField(default=False)
    user_banner_url = models.URLField(max_length=200, blank=True)
    user_roles = models.ManyToManyField("Role", default='None', blank=True)
    user_history = HistoricalRecords(cascade_delete_history=True)

    class Meta:
        verbose_name = ("User")
        verbose_name_plural = ("Users")

    def __str__(self):
        return self.user_name

    def save(self, *args, **kwargs):
        self.user_guilds_count = self.user_guilds.count()
        self.user_messages_count = Message.objects.filter(message_author=DiscordUser.objects.get(user_id=self.user_id)).count()
        super(DiscordUser, self).save(*args, **kwargs) # Call the "real" save() method.

    def get_absolute_url(self):
        return reverse("user", kwargs={"pk": self.pk})

class GuildChannel(models.Model):

    channel_name = models.CharField(max_length=50, editable=False, verbose_name='Channel name')
    channel_id = models.DecimalField(max_digits=25, decimal_places=1, unique=True, verbose_name='Channel ID')
    channel_guild = models.ForeignKey("Guild", on_delete=models.CASCADE, verbose_name=("Guild"))
    channel_category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, default='None', verbose_name='Category')
    channel_text = models.BooleanField(default=False, verbose_name='Is text?')
    channel_history = HistoricalRecords(cascade_delete_history=True)

    class Meta:
        verbose_name = ("Channel")
        verbose_name_plural = ("Channels")

    def __str__(self):
        return self.channel_name

    def get_absolute_url(self):
        return reverse("GuildChannel_detail", kwargs={"pk": self.pk})

class Guild(models.Model):

    guild_name = models.CharField(max_length=120, verbose_name='Guild Name')
    guild_id = models.DecimalField(max_digits=20, decimal_places=0, unique=True, verbose_name='Guild ID') # Technical field
    guild_description = models.TextField(blank=True, default='None', verbose_name='Guild description', null=True)
    guild_members = models.IntegerField(default=0, verbose_name='Guild members')
    guild_channels = models.IntegerField(default=0, verbose_name='Guild channels')
    guild_categoriest = models.IntegerField(default=0, verbose_name='Guild categories')
    guild_roles = models.IntegerField(default=0, verbose_name='Guild roles')
    guild_owner = models.ForeignKey(DiscordUser, on_delete=models.CASCADE, default=None, blank=True, null=True)
    guild_region = models.CharField(max_length=40, default='None')
    guild_default_role = models.ForeignKey('Role', default=1, on_delete=models.CASCADE)
    guild_large = models.BooleanField(default=False, verbose_name='Is large')
    guild_verification_level = models.IntegerField(default=0, verbose_name='Verification level')
    guild_mfa_level = models.IntegerField(default=0)
    guild_created_at = models.DateField(blank=True, default=0, verbose_name='Created at')
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
        if Message.objects.filter(message_guild = self).exists(): 
            self.guild_messages = Message.objects.filter(message_guild = self).count()
        else: self.guild_messages = 0
        if DiscordUser.objects.filter(user_guilds = self).exists(): 
            self.guild_members = DiscordUser.objects.filter(user_guilds = self).count()
        else: self.guild_members = 0
        super(Guild, self).save(*args, **kwargs) # Call the "real" save() method.

    def get_absolute_url(self):
        return reverse("guild", kwargs={"pk": self.pk})

class Category(models.Model):

    category_name = models.CharField(max_length=50, verbose_name='Category')
    category_id = models.DecimalField(max_digits=20, decimal_places=0, unique=True, verbose_name="Category ID", null=True)
    category_guild = models.ForeignKey(Guild, verbose_name='Guild', null=True, on_delete=models.CASCADE, blank=True)
    category_history = HistoricalRecords(cascade_delete_history=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.category_name

    def get_absolute_url(self):
        return reverse("сategory", kwargs={"category_id": self.pk})

class Role(models.Model):

    role_name = models.CharField(verbose_name='Role name', max_length=120)
    role_is_default = models.BooleanField(default=False)
    role_id = models.DecimalField(max_digits=20, decimal_places=0, unique=True, verbose_name='Role ID', null=True)
    role_guild = models.ManyToManyField(Guild, default='None', blank=True, verbose_name='Role guild')
    role_color = ColorField(default='#000000', verbose_name='Role color')
    role_history = HistoricalRecords(cascade_delete_history=True)

    class Meta:
        verbose_name = ("Role")
        verbose_name_plural = ("Roles")

    def __str__(self):
        return self.role_name

    def get_absolute_url(self):
        return reverse("role_detail", kwargs={"pk": self.pk})

class Message(models.Model):

    message_content = models.TextField(verbose_name='Content')
    message_author = models.ForeignKey(DiscordUser, on_delete=models.CASCADE, blank=True)
    message_id = models.DecimalField(max_digits=30, decimal_places=0, unique=True, verbose_name='Message ID', null=True, editable=False)
    message_channel = models.ForeignKey(GuildChannel, on_delete=models.CASCADE, blank=True, default="None", verbose_name='Channel')
    message_category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, default="None", verbose_name='Category')
    message_guild = models.ForeignKey(Guild, on_delete=models.CASCADE, blank=True, default="None", verbose_name='Guild')
    message_pinned = models.BooleanField(default=False, verbose_name='Is pinned')
    message_jump_url = models.URLField(editable=False, verbose_name='Jump url')
    message_date = models.DateField(auto_now_add=True, editable=False, verbose_name='Created at')

    class Meta:
        verbose_name = ("Message")
        verbose_name_plural = ("Messages")

    def __str__(self):
        cont = f"Message\nAuthor: {self.message_author}\nGuild: {self.message_guild}\nContent: {self.message_content}"
        return cont

class Emojis(models.Model):

    emoji_name = models.CharField(max_length=255, verbose_name='Emoji name')
    emoji_photo = models.URLField(editable=False, verbose_name='Photo')
    emoji_animated = models.BooleanField(default=False, verbose_name='Is animated')
    emoji_guild = models.ForeignKey(Guild, on_delete=models.CASCADE, default=None, blank=True, verbose_name='Emoji Guild')
    emoji_id = models.DecimalField(max_digits=30, decimal_places=0, unique=True, verbose_name='Emoji ID', null=True, editable=False)
    role_history = HistoricalRecords(cascade_delete_history=True)

    class Meta:
        verbose_name = ("Emoji")
        verbose_name_plural = ("Emojies")

    def __str__(self):
        return self.emoji_name

class Polls_option(models.Model):

    option_name = models.CharField(max_length=255, verbose_name='Option name')
    option_guild = models.ForeignKey(Guild, on_delete=models.CASCADE, blank=True, verbose_name='Option guild')
    option_voters = models.ManyToManyField(DiscordUser, default='None', blank=True)
    option_poll = models.ForeignKey('Polls', on_delete=models.CASCADE, blank=True, default=0, verbose_name='Option poll')

    class Meta:
        verbose_name = 'Poll Option'
        verbose_name_plural = 'Poll Options'

    def __str__(self):
        return self.option_name

class Polls(models.Model):

    polls_id = models.DecimalField(max_digits=30, decimal_places=0, unique=True, verbose_name='Poll ID', null=True, editable=False)
    polls_name = models.CharField(max_length=255, verbose_name='Poll name')
    polls_author = models.ForeignKey(DiscordUser, on_delete=models.CASCADE, blank=True, verbose_name='Poll author')
    polls_participants = models.ManyToManyField(DiscordUser, related_name='polls_participants', blank=True, verbose_name='Poll participants')
    polls_options = models.ManyToManyField(Polls_option, related_name='options_available',default='None', blank=True)
    polls_time = models.DateTimeField(verbose_name='End time')
    polls_created_at = models.DateField(auto_now_add=True, null=True, verbose_name='Created at')
    polls_guild = models.ForeignKey(Guild, on_delete=models.CASCADE, blank=True, verbose_name='Poll guild')
    poll_winner = models.ForeignKey(Polls_option, related_name='options_winner', on_delete=models.CASCADE, blank=True, null=True, verbose_name='Poll winner')
    poll_history = HistoricalRecords()

    class Meta:
        verbose_name = ("Poll")
        verbose_name_plural = ("Polls")

    def __str__(self):
        return self.polls_name

    def get_absolute_url(self):
        return reverse("polls", kwargs={"pk": self.pk})

class Giveaways(models.Model):

    giveaway_id = models.DecimalField(max_digits=30, decimal_places=0, unique=True, verbose_name='Giveaway ID', null=True, editable=False)
    giveaway_item = models.CharField(max_length=255, verbose_name='Giveaway item')
    giveaway_author = models.ForeignKey(DiscordUser, on_delete=models.CASCADE, blank=True, verbose_name='Giveaway author')
    giveaway_time = models.DateTimeField(verbose_name='End time')
    giveaway_created_at = models.DateField(auto_now_add=True, null=True, verbose_name='Created at')
    giveaway_guild = models.ForeignKey(Guild, on_delete=models.CASCADE, blank=True, verbose_name='Giveaway guild')
    giveaway_winner = models.ForeignKey(DiscordUser, related_name='user_winner', on_delete=models.CASCADE, blank=True, null=True, verbose_name='Giveaway winner')
    poll_history = HistoricalRecords()

    class Meta:
        verbose_name = ("Giveaway")
        verbose_name_plural = ("Giveaways")

    def __str__(self):
        return self.giveaway_item

    def get_absolute_url(self):
        return reverse("polls", kwargs={"pk": self.pk})

class Bot(models.Model):

    bot_update = models.DateTimeField()
    bot_name = models.CharField(default=None, blank=True, max_length=255)

    class Meta:
        verbose_name = ("Bot")
        verbose_name_plural = ("Bots")

    def __str__(self):
        return self.bot_name

    def get_absolute_url(self):
        return reverse("bot_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        self.bot_update = timezone.localtime(timezone.now())
        super(Bot, self).save(*args, **kwargs) # Call the "real" save() method.

