from tortoise.models import Model
from tortoise import fields


class Account(Model):
    id = fields.IntField(pk=True)
    username = fields.TextField()
    chips = fields.BigIntField()

    def __str__(self):
        return self.username
