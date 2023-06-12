import telegram.ext.dispatcher as dispatcher
from telegram import TelegramError

class GatekeepingDispatcher(dispatcher.Dispatcher):

    def __init__(self, gatekeeping_strategy, *args, **kwargs):
        super(GatekeepingDispatcher, self).__init__(*args, **kwargs)

        self.gatekeeping_strategy = gatekeeping_strategy

    def process_update(self, update):
        # If we have no strategy configured, always forward all updates
        if self.gatekeeping_strategy is None:
            super().process_update(update)
            return

        # Let the dispatcher handle errors
        if isinstance(update, TelegramError):
            super().process_update(update)
            return

        effective_update = self.gatekeeping_strategy.pass_update(self.bot, update)
        if effective_update is not None:
            super().process_update(effective_update)
            return