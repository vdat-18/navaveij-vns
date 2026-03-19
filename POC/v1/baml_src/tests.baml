function CredentialSmokeTest() -> string {
  client NavaveijClient
  prompt #"
    {{ _.role("system") }}
    You are a test assistant.
    {{ _.role("user") }}
    Reply with exactly: PONG
"#
}

test CredentialsWork {
  functions [CredentialSmokeTest]
  args {
  }
  @@assert( {{ this|trim == "PONG" }} )
}
