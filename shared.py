class Shared:
        def __init__(self):
                # anything that needs to be shared between cogs
                # goes here
                self.heists = set()
                # anyone in this set cannot be robbed
                self.rob_lock = set()

shared = Shared()