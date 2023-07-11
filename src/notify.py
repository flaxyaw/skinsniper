from discord_webhook import DiscordWebhook, DiscordEmbed
from config import notify

def notify_send(message):
    webhook_url = notify["webhook_url"]
    webhook = DiscordWebhook(url=webhook_url)

    embed = DiscordEmbed(description=message)
    embed.set_author(name="Notification")
    embed.set_footer(text="Powered by Discord Webhook")

    webhook.add_embed(embed)
    response = webhook.execute()
    if response.status_code != 204 and response.status_code != 200:
        print("Failed to send webhook: " + str(response.status_code))
