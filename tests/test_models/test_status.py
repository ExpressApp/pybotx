import uuid

from botx import ChatTypes
from botx.models.status import StatusRecipient


def test_status_recipient():
    bot_id = uuid.uuid4()
    user_huid = uuid.uuid4()
    ad_login = "login"
    ad_domain = "domain"
    is_admin = True
    chat_type = ChatTypes.chat
    recipient = StatusRecipient(
        bot_id=bot_id,
        user_huid=user_huid,
        ad_login=ad_login,
        ad_domain=ad_domain,
        is_admin=is_admin,
        chat_type=chat_type,
    )
    assert recipient.bot_id == bot_id
    assert recipient.user_huid == user_huid
    assert recipient.ad_login == ad_login
    assert recipient.ad_domain == ad_domain
    assert recipient.is_admin == is_admin
    assert recipient.chat_type == chat_type
