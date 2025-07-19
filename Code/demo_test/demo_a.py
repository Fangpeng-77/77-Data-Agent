from zhipuai import ZhipuAI

client = ZhipuAI(api_key="") # 请填写您自己的APIKey
response = client.chat.asyncCompletions.create(
    model="glm-4",  # 请填写您要调用的模型名称
    messages=[
        {
            "role": "user",
            "content": "作为童话之王，请以始终保持一颗善良的心为主题，写一篇简短的童话故事。故事应能激发孩子们的学习兴趣和想象力，同时帮助他们更好地理解和接受故事中蕴含的道德和价值观。"
        }
    ],
)
print(response)