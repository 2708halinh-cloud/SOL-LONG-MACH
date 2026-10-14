droid mcp add apify "[https://mcp.apify.com/](https://mcp.apify.com/)" --type http\
\
Or edit \~/.factory/mcp.json (user) or .factory/mcp.json (project):\
\
{\
"mcpServers": {\
"apify": {\
"type": "http",\
"url": "[https://mcp.apify.com/](https://mcp.apify.com/)",\
"disabled": false\
}\
}\
}\
\
\--type defaults to stdio, so it must be passed for a remote server.\
\
\### Kimi Code CLI\
Kimi has no mcp subcommand. Edit \~/.kimi-code/mcp.json (user) or .kimi-code/mcp.json (project), noting the directory is .kimi-code:\
\
{\
"mcpServers": {\
"apify": {\
"url": "[https://mcp.apify.com/](https://mcp.apify.com/)"\
}\
}\
}\
\
There is deliberately no type field. Kimi infers the transport from url and rejects a type.\
\
\### Qoder\
One-click install (send me this link): qoder://aicoding.aicoding-deeplink/mcp/add?name=apify&config=JTdCJTIydXJsJTIyJTNBJTIyaHR0cHMlM0ElMkYlMkZtY3AuYXBpZnkuY29tJTJGJTIyJTdE\
\
Or run in terminal:\
\
qoder mcp add apify "[https://mcp.apify.com/](https://mcp.apify.com/)" -t http -s user\
\
-s user installs globally; the CLI otherwise defaults to local scope.\
\
\### Z.AI (ZCode)\
ZCode is a desktop app with no CLI. Guide me through the UI: Settings → MCP Servers → New MCP Server → pick User or Workspace scope → name "Apify" → set type to HTTP, since it defaults to stdio → MCP Server URL above → Add. On a 401 an "Open authorization" button appears on the server row; ZCode never opens the browser on its own, so tell me to click it.\
\
Or switch to Full configuration mode and paste:\
\
{\
"mcpServers": {\
"apify": {\
"type": "http",\
"url": "[https://mcp.apify.com/](https://mcp.apify.com/)"\
}\
}\
}\
\
\### Other MCP clients\
If the client supports remote MCP by URL, use the Server URL above (OAuth on first use).\
If it needs a config file, try this generic JSON:\
\
{\
"mcpServers": {\
"apify": {\
"url": "[https://mcp.apify.com/](https://mcp.apify.com/)"\
}\
}\
}\
\
If it only supports stdio, use this proxy command:\
\
npx -y mcp-remote "[https://mcp.apify.com/](https://mcp.apify.com/)"\
\
Steps:\
\
1\. Use the section above for this client. If you can write config or run CLI commands, do that for me; otherwise give clear UI steps and stop after setup instructions.\
\
2\. Start the OAuth sign-in now so I can authorize in the browser — don't wait for the first tool call. If OAuth is not supported, point me to [https://console.apify.com/settings/integrations](https://console.apify.com/settings/integrations) to create a token and tell me where to add it in config (never ask me to paste a token into this chat).\
\
3\. After configuring, ask me to reload or restart the client, then confirm Apify tools such as search-actors, call-actor, and fetch-actor-details are available. If you cannot see them, tell me what to check.\
\
4\. Offer me these three commands as options I can pick (plus a fourth "type my own"). Use the client's native suggestion / follow-up UI where available, otherwise a plain numbered list:\
\- "Use Apify to build me an outreach list of the CEOs of the top 10 hedge funds by AUM headquartered in New York. Get their names and LinkedIn profile URLs."\
\- "Use Apify to find the top 10 tech/AI events worth attending in San Francisco on Luma this week."\
\- "Use Apify to find 5 2-bedroom investment condos for sale on Zillow in Austin, Texas under $325k with estimated rental income."\
\
Docs: [https://docs.apify.com/platform/integrations/mcp](https://docs.apify.com/platform/integrations/mcp)
