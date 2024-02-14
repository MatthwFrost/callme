from twilio.rest import Client

# Your Twilio account SID and auth token
account_sid = 'AC3a20d73c12b20354cf078e36372da3f4'
auth_token = 'f55a1623251d3e988e580321406bc7b1'
client = Client(account_sid, auth_token)

call = client.calls.create(
    to="+447568085248",
    from_="+447488898561",
    url="https://0615-82-21-153-151.ngrok-free.app/gather_response"
)

print(call.sid)

