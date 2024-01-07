from b2sdk.v2 import InMemoryAccountInfo
from b2sdk.v2 import B2Api

import os



info = InMemoryAccountInfo()  

b2_api = B2Api(info)
b2_api.authorize_account("production", os.getenv("B2_ACCOUNT_ID"), os.getenv("B2_APPLICATION_KEY"))