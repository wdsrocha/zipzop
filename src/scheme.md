
```js
client
    type login
    data {
        nickname
        public_key
    }

    type logoff
    data

    type say
    data {
        [
            public_key
            message
        ]
        message
    }

server
    type login_response
    data {
        [
            nickname
            public_key
        ]
    }

    type new_user
    data {
        nickname
        public_key
    }

    type say
    data {
        nickname
        text
    }

    type announce
    data {
        nickname
        text
    }
```