import asyncio


class PokerTimer:
    def __init__(self, timeout, callback):
        self.timeout = timeout
        self.callback = callback
        self.timer_task = None

    async def start(self):
        await asyncio.sleep(self.timeout)
        self.callback()

    def reset(self):
        if self.timer_task and not self.timer_task.done():
            self.timer_task.cancel()
        self.timer_task = asyncio.create_task(self.start())


# Example usage:
def player_timeout_callback():
    print("Player's time is up!")


async def main():
    # Create a timer with a timeout of 60 seconds and the callback function
    timer = PokerTimer(1, player_timeout_callback)

    # Start the timer
    await timer.start()

    # Reset the timer if needed (e.g., when the player makes a move)
    timer.reset()


# Run the event loop
asyncio.run(main())
