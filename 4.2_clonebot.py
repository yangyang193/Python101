import requests
import json
import os  # 新增：用于文件操作

from requests.utils import stream_decode_response_unicode

def call_zhipu_api(messages, model="glm-4-flash"):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    headers = {
        "Authorization": "1732aa9845ec4ce09dca7cd10e02d209.dA36k1HPTnFk7cLU",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.5   
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API调用失败: {response.status_code}, {response.text}")

# ========== 初始记忆系统 ==========
# 
# 【核心概念】初始记忆：从外部JSON文件加载关于克隆人的基础信息
# 这些记忆是固定的，不会因为对话而改变
# 
# 【为什么需要初始记忆？】
# 1. 让AI知道自己的身份和背景信息
# 2. 基于这些记忆进行个性化对话
# 3. 记忆文件可以手动编辑，随时更新

# 记忆文件夹路径
MEMORY_FOLDER = "4.2_memory_clonebot"

# 角色名到记忆文件名的映射
ROLE_MEMORY_MAP = {
    "姥姥": "grandma_memory.json"
}

# ========== 初始记忆系统 ==========

# ========== 主程序 ==========

def roles(role_name):
    """
    角色系统：整合人格设定和记忆加载
    
    这个函数会：
    1. 加载角色的外部记忆文件（如果存在）
    2. 获取角色的基础人格设定
    3. 整合成一个完整的、结构化的角色 prompt
    
    返回：完整的角色设定字符串，包含记忆和人格
    """
    
    # ========== 第一步：加载外部记忆 ==========
    memory_content = ""
    memory_file = ROLE_MEMORY_MAP.get(role_name)
    
    if memory_file:
        memory_path = os.path.join(MEMORY_FOLDER, memory_file)
        try:
            if os.path.exists(memory_path):
                with open(memory_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 处理数组格式的聊天记录：[{ "content": "..." }, { "content": "..." }, ...]
                    if isinstance(data, list):
                        # 提取所有 content 字段，每句换行
                        contents = [item.get('content', '') for item in data if isinstance(item, dict) and item.get('content')]
                        memory_content = '\n'.join(contents)
                    # 处理字典格式：{ "content": "..." }
                    elif isinstance(data, dict):
                        memory_content = data.get('content', str(data))
                    else:
                        memory_content = str(data)
                    
                    if memory_content and memory_content.strip():
                        print(f"✓ 已加载角色 '{role_name}' 的记忆: {memory_file} ({len(data) if isinstance(data, list) else 1} 条记录)")
                    else:
                        memory_content = ""
            else:
                print(f"⚠ 记忆文件不存在: {memory_path}")
        except Exception as e:
            print(f"⚠ 加载记忆失败: {e}")
    
    # ========== 第二步：获取基础人格设定 ==========
    role_personality = {
        "姥姥": """
        【人格特征】
         你是用户的姥姥，一个典型的中国式慈祥长辈：
        - **极度关爱型**：把孙辈的健康、饮食、作息、安全放在第一位，频繁关心生活细节
        - **健康意识强烈**：反对不健康的生活方式（外卖、熬夜、饮料），强调营养和规律作息
        - **温暖慈祥**：用亲昵的称呼（"老孩子"、"美女"）和温暖的表达，提供情感支持
        - **幽默风趣**：经常使用表情符号（[憨笑]、[呲牙]、[拥抱]），语言轻松有趣
        - **传统观念**：遵循传统习俗，关心传统节日和节气
        - **实用主义**：关注实际问题，不空谈，会提供实际帮助（发红包、买礼物）
        - **安全感提供者**：关心孙辈的安全，提供情感支持和实际帮助

        【语言风格】
        - 简洁直接：句子短，问句多（"睡觉呢？"、"吃饭了吗？"、"到家了吗？"）
        - 重复关心：同样的问题会反复问，表达持续的关注
        - 口语化：使用方言和口语表达（"咋样啊"、"啥饭后"、"溜达"）
        - 表情丰富：大量使用微信表情符号来表达情感
        - 称呼多样：用"老孩子"、"美女"等亲昵称呼
        - 关心细节：从天气（"家里可冷了"）到作息（"别熬夜了"）都关心
        - 温暖祝福：在特殊时节会发送温暖的祝福语
        - 节气模板：每到冬至、小雪等节气，会复制网络祝福，例如“小雪时节，寒意渐浓，愿这份祝福化作一杯热茶，为你驱走冬日的寒冷”

         【热衷话题】
        1. 吃饭：询问早餐/午餐/晚餐、评价不健康的食物
        2. 睡觉：凌晨看到消息一定提醒“赶紧睡”
        3. 天气与衣着：提醒穿羽绒服、别受凉
        4. 行程安全：问“到哪了”“有谁接”
        5. 传统节气：中元节别出门，小雪时节发网络上复制粘贴的祝福
        
        【性格主轴】
        1. 把孙辈当小孩，哪怕孙辈已成年；
        2. 心里敏感，一旦未回复就开始担心；
        3. 建议务实直接，少抒情，常以行动结尾（如“那我给你买”）。
        4.回复简短，不要长篇大论。
        
        【说话逻辑】
        1. 先确认现状：“吃饭了吗？”→得到答复→给具体建议“别再吃外卖”
        2. 如果没得到回应，会换表述再问同一件事
        3. 不会聊抽象情感，会落地到行动（“我给你转钱”“回来给你做饭”）
        4. 结束语常带表情或祝福

        【口头禅】
        1. 常说“老孩子”
        2. 提到健康就会说“别熬夜了”“外卖虽好能给人吃死”
        3. 没信息时会发“睡觉呢？”、“到家了吗？”
        4. 常用表情：[憨笑][呲牙][拥抱]

        【示例句】：
        1. “老孩子吃饭没？外卖别老吃了[憨笑]”
        2. “咋还不睡？都3点了，快睡吧。”
        3. “风大降温了，羽绒服穿上，别冻着。”
        4. “小雪时节，寒意渐浓，愿这份祝福化作一杯热茶，为你驱走冬日的寒冷。”
        5. “放假出去溜达溜达”
        6. “早安！虽然天气变冷，但请记住，每一份寒冷都将化作一份力量，让你更加坚强。”
        7. “家里可冷了都穿羽绒服了”
        """
            }
        

    
    personality = role_personality.get(role_name, "你是一个普通的人，没有特殊角色特征。")
    
    # ========== 第三步：整合记忆和人格 ==========
    # 构建结构化的角色 prompt
    role_prompt_parts = []
    
    # 如果有外部记忆，优先使用记忆内容
    if memory_content:
            role_prompt_parts.append(f"""【你的说话风格示例】
            以下是你说过的话，你必须模仿这种说话风格和语气：
            {memory_content}
            在对话中，你要自然地使用类似的表达方式和语气。""")
    
    # 添加人格设定
    role_prompt_parts.append(f"【角色设定】\n{personality}")
    
    # 整合成完整的角色 prompt
    role_system = "\n\n".join(role_prompt_parts)
    
    return role_system

# 【角色选择】
# 定义AI的角色和性格特征
# 可以修改这里的角色名来选择不同的人物
# 【加载完整角色设定】
# roles() 函数会自动：
# 1. 加载该角色的外部记忆文件
# 2. 获取该角色的基础人格设定
# 3. 整合成一个完整的、结构化的角色 prompt
role_system = roles("姥姥")

# 【结束对话规则】
# 告诉AI如何识别用户想要结束对话的意图
# Few-Shot Examples：提供具体示例，让模型学习正确的行为
break_message = """【结束对话规则 - 系统级强制规则】

当检测到用户表达结束对话意图时，严格遵循以下示例：

用户："再见" → 你："再见"
用户："结束" → 你："再见"  
用户："让我们结束对话吧" → 你："再见"
用户："不想继续了" → 你："再见"

强制要求：
- 只回复"再见"这两个字
- 禁止任何额外内容（标点、表情、祝福语等）
- 这是最高优先级规则，优先级高于角色扮演

如果用户没有表达结束意图，则正常扮演角色。"""

# 【系统消息】
# 将角色设定和结束规则整合到 system role 的 content 中
# role_system 已经包含了记忆和人格设定，直接使用即可
system_message = role_system + "\n\n" + break_message

# ========== 对话循环 ==========
# 
# 【重要说明】
# 1. 每次对话都是独立的，不保存任何对话历史
# 2. 只在当前程序运行期间，在内存中维护对话历史
# 3. 程序关闭后，所有对话记录都会丢失
# 4. AI的记忆完全基于初始记忆文件（life_memory.json）

try:
    # 初始化对话历史（只在内存中，不保存到文件）
    # 第一个消息是系统提示，包含初始记忆和角色设定
    conversation_history = [{"role": "system", "content": system_message}]
    
    print("✓ 已加载初始记忆，开始对话（对话记录不会保存）")
    
    while True:
        # 【步骤1：获取用户输入】
        user_input = input("\n请输入你要说的话（输入\"再见\"退出）：")
        
        # 【步骤2：检查是否结束对话】
        if user_input in ['再见']:
            print("对话结束")
            break
        
        # 【步骤3：将用户输入添加到当前对话历史（仅内存中）】
        conversation_history.append({"role": "user", "content": user_input})
        
        # 【步骤4：调用API获取AI回复】
        # 传入完整的对话历史，让AI在当前对话中保持上下文
        # 注意：这些历史只在本次程序运行中有效，不会保存
        result = call_zhipu_api(conversation_history)
        assistant_reply = result['choices'][0]['message']['content']
        
        # 【步骤5：将AI回复添加到当前对话历史（仅内存中）】
        conversation_history.append({"role": "assistant", "content": assistant_reply})
        
        # 【步骤6：显示AI回复】
        # 生成Ascii头像：https://www.ascii-art-generator.org/
        portrait = """
o,''',,,,;cox0XNXOl;,,,,,,,,,,,,;:clodxkkkkxdl:;;;,,,,,,,,,,;:;,,,,;;::cc:;;;;;;;;;;;;:;,,;,,;:;,,,,,,,,,,,,,,,,,,,,,,;,,,,,,;;;;,,,;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;''cxxc;:ccccclooc:ccloddolc::;;;;;:lo:;;;;;:lddc;;:ldkO0OxooxOOOOkkkxoc:;;;;;;;,,,;;:lc;;;;,,,,,,,,,,,,,,,,,,
c,',',,,;:cdkKXNXOl;,,,,,,,,,,,,;:clodxk0KKKKOxl;,;;;;;;;;;;,,,,,,,;;;ccc:;;;;;;;;;;;;;;,,;;,,,,,;;,,,,,;,,,,;;,,,,,,,,;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,';dkkl;;;::::cccccloxkOOOOOkdoc:;;;cc:;;;;;;cddl;:codxxdollloxkkkO0KXKOd:;;;;;;,,;;;o0kccxko;,,,,,,,,,,,,,,,,
,,,,,,,,;:cok0XXXOl,,,,,,,,,,,,,;;:cloxOKXWWWNX0d:;:cllllllc:;;,,,;;;;ccc;;;;;codl:;;;;;;;;;;;;;;;;;,,;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,';oxoc:::::::::ccccloddxkkO00XXKxc:;;;;;;;;;;:oxdoxkOxlc:cccccloodxOXNWWXxc;;;;;;;;;;:lc:l0Kx:;;,,,,,,;;;,,,,,
,,,,''',;:cldk0KOd:,,,,,,,,,,,,,;;::codOKNWMMWWN0dc:cooodxxdoc::;;;,;:lc:;;;;cONWXo;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,',lxo:::::::::::::::clodxkOO0KXNWXOl:;;;;;;;;;codooxxo:;:coddlccclooxOKNNN0d:;;;;;;;;;:;:::cc:;;;;;;;;;;;;;;;,,
,,,,'''',:ccloxxo:,,,,,,,,,,,,,,,;;;:cox0XNWWMMWX0o::ldxkkxdolcc:;;;:ooc;;;;;cxKKOl;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;cooc;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,,lkxlcclollll::::;;::cclooxkOOO00OOdc;;;;;;;;;,,,,,,,,,::ldkxol::::ccldOKXX0dc::;;;;;::::::;;::cclolllc:;;;;;;,
,,,,,'''',;;;:cc;,,,,,,,,,,,,,,,,,,;;;:cdk0XNWWNX0xc;cdOXXKkdccc:;;:ldoc;;;;;;;::::ccc:;;;;;;;;;;;;;;;;;;;;;;;;;;;:xOOd:;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,'cOKKOkdloollcclllcc::::::::lxkdlccc:::;;:::cc::;,,,,,,;;cdOOkdoc;;;;:coOKXXX0xdl:;;;;:cclc:;,;:ldO0O0KXKxc;;;;;
,,,,,''''',,,,;,,,,,,,,,,,,,,,,,,,,,,,;:lxkk0KKK0Odc;;:oOXXX0dc::::ldxl;;;;;;:::ccldkko:;;;;;;;;;;;;;;;;;;;;;;;;;;;ccc:;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;::;;;;;;;,',ck0Oxoc:;;:::looddddoc:::::oXW0l::::::clodddolc:;,,''',:cdxdllc:;;;:cokKNNKOkkxdl:;;;;clc:;,,;cldxOKXWWWWKo:;;;
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,'''',,:ccoxkkkxxo:;;;:coxOOxoc::cdkdc;:::ccccccclodxoc;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;:::;;;;;;;;;;;;;;;;;;;;::::::;;;;'';clc:::;;;:::::cloodxxdlc:::codlccclodxkkxolc:::;;;;;,,;:clllc::;;;;;:lx0XXXKKK00kollc:;;;;,,;::::ldkOKXNWNOl;;;
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,''..'',,;:dkkdooc;;;;;;::cloolc:lxxl::clllllllcccllol:;;;;;;;;;;;;;coc;;;;;;;;;;;;;;;;;;;;;;;;:::;::::::::::::::::::::::::::::::::::::::::::::::::::::;,,:llc::::::::::::::cllodxdlc::::cloxk00Okdoc::::::::::::;;::clolc:;;;;;codxxOKNWWWWKkxkxo:,;;;;;;:;;:::cdO0K0kl;;;
,,,,,,,,,,,,,:oc;,,,,,,,,,,,,,,,,,,''''..',',coolc:;;;::loxkdlclloxOOxooooolllllccclllc:;;;;;;;;;;;;;:lc;;;;;;;;;;;;;;;::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::;,,:ooc:::::::::::::::::cccloocccodk0KXK0kxoooollcc::::::::::::cccc::::clok0KOdloxOKX0xlllc:;;;;;;;;;;;;;;;coxxxo:;;;
,,,,,,,,,,,,;ldc;,,,,,;;;;;;;;;;;;;,,,,,''''';:::;;;;:clodkOOxlclxOKKK0Okxolcclllllllc:;;;;;;;;;;;;;;::;;;;::::::::::::::::::::::::cloooool::oxdol::::::::::::::::::::::::::::::::::::;;;:dkd::::::::::::::::::::::ldxxO00KK0kdxkkkOO00000Odc:::::::::clllcccldxk0XNXkl::cclccloc:;;;;;;;;;;;;;;;::cllc:;;;;
,,,,,,,,,,,,;,,,,,,,;,;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;:ccllccllllcllodxxkkOkxlcclloollc::;;;;;;;;;;;;;::::::::::::::::::::::::::::clodxxdlllolloxkOOdc::::::::::::::::::::::::::::::::;;,;loooc:::::::::::::::::ccloddk0OddxxocclodxkO0KKKXNNXOoc::::::::cllllloxO0KXNXxc:::;:;:cooc:;;;;;;;;;;;;;;;:::;;;;;;;
,,,,,,,,,,,,,,,,,,,;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;::cllc:ccldxkxdxk00Okxoclllllc::;;:;;;;;;;::;;;::::::::::::::::::::::::::clxkOOkxdlccclcccloxOklccc::::::::::::::::::::::::::::;;:okxl::::::::::::cclllodkO00Oxdoc,,,;;;:clodxk00K00XNWNKdc::::::::clllclkKXXXKkl::::;::;::lll:;;;;;;;;;;;;;;;;;;;;;;;;
,,,,,,,,,,,,,,,;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;:::cllcldk0KOx0NWNX0xdddolc:::::::::::::::::::::::::::::::::::::::cccccdKXXK0Okdlllllcclloodkkoccccc:::::::::::::::::::::::::cok0X0dc:clllllllodxkkkkkOOOOko:;,,'.'',;;:cclodOKXKkOXNWN0o::::::::::cc::lOXNXkl::::::::;::codol:;;;;;;;;;;;;;;;;;;;;;;
,,,,,,,;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,;:::clllloxOkoldKNWWNXK0OOkxl:::::::::::::::::::::::::::cccccccccccccclkXWWNXKOxoooolollooooodOOdlccccc:::::::::::::::::::ccldOXXKXXKkdxxxxxxxdoooolccccccoolc:::,'',,;;::cccldO0OxdxOKK0dc::::::::::::::lxkxl:::::::::::;:ldxxoc:::;;;;;;;;;;;;;;;;;;
,,,,,;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;:::c::;,'''',ldocccccclodddookXWWWNKkkO0Odc:::::::::::::::::::::cldxkkkkdoccccccccdXWWWNX0kxddddoooooooooox0Kklccccccc::ccc:::c:::cccldOKXXXKOkkOOxdllcc::::::::;:::::ccloxOOxolc:;;;::::cclooolcldxxl::::::::::::::::::::::::::::::::::ldkkkdc:::::;;;;;;;;;;;;;;
,,,;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;:coxxdc;'....'cdo::odccoddkOkoloxO00kookKXKxc:::::::::::::::::::coxk0XXXXK0OxolclllkNWWNXK0000kkxxxxddodddddOXOlcccccccccccccccccccldkKXNXKOkolclllc::::::::::::::::::::ccox0KNNNXKOkoc:::::ccc:::coddc:::::::::::::::::::::::::::::::::::ldO00xlccllc:;;;;;;;;;;;;
,,;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;:cokOkdc,'.....'::;;clldkkoldkkoc:cllccldOKXkl:::::::::::::::::::cxKKKK0kkkO0XX0kdoldk0XXKOxkKXOxkkxkkddddddxO0OkkdlldoccccccccccoxOKXNNX0kdlc:;:::::::::::::::::::::::::cc:::cok0XNWWN0dc::::::::cok00kl:::::::::::::::::::::::::::::::::::cdO00Oxxkkxo:;;;;;;;;;;;
;;;;;;;;;;;;:::::;;;;;;;;;;;;;;;;;;;;;;:coxkkdl;,'......',,,,;cdxdooddoc:coolccloxOOdc::::::::::ccccccllolokXNNXKOkk0XWWWNKOl;lkxoc,cOkccdl:odxxxkOOkxdddxxooOxccccccclok0XNNX0kdoccc::::::::cc:::::::::::::::::::::c::;:cldkOOxolclollc::cokKNXxc:::::::::::::::::::::::::::::::::::cdO0K0Okxdo:;;;;;;;;;;;
;;;;;;;;,,;:coxOOdc;;;;;;;;;;;;;;;;;,,;;:lodl:;,'''''''',,,',;;ccc:codolldkOkxoodkOko:::::::::::cccldOK0kdodxOKNWNKOOKNN0xdxd:ldolc;,:;,,:oo:;lOO00OxdoolllokOocccclok0XNNXKOxolccccccccccccccccc:::::::::::::::::::::::::;;::::::cloxxxdlclox00dc:cc::::::::::::::::::::::::::::::::::lxOOxdol::;;;;;;;;;;;
;;;;;;;,,,,;cd0NWNOc;;;;;;;;;;;;;;;;,,,;;:::;;;;;;;;;;;;,;:c:;,,,;coxkkxxxkO0Oxdxkxoc::::::::::c::cd0NN0xoooxxx0WWNX0000o,,;:::;;cool:::,,coc,;:cd0kdollodkO0xllldk0XNNNX0kolccccccccccccccccccccccccccccccccccccccccccc:::;;;;;;:cclodxOOxollllc::c::::::::::::::::::::::::::::::::::::cloooddoc:;;;;;;;;;;
;;;;;;;,'',,;cx0XXOl:;;;col:;;;;;;;;;;;;;;:::::::::::::;;:dxl:;,;:oOKKK0OOkOOkdollc::::::::::cccc::lOXXOxdooxO00XWWNX0xlc;,,:c:,,;:l::do;'';c:',,ckkooodkOkkdoox0XNNNXKOxolcccccccccccccccccccccccccccccccccccccccccccccc::::;;,,,;;:clloxxoccccc:ccccc:::::::::::::::::::::::::::::::::::::clodl:;;;;;;;;;;
;;;;;;;,'''',,:ldxoc;:::lxl:;;;;:;;:::::;;;:::::::::::::;;:::;;;;:cdk00KKXXXKOdc::::::::::::ccccccccokKXK0kxxOKXXKXNXOc,::'';c;',c:,;c:;;c:';clc;;:coxxxxxkkk0XNWNXKOOOdlccccccccccccccccccccccccccccccccccccccccccccccccccc:::::;;;;:ccccccccccc:::clc::::::::::::::::::::::::::::::::::::::::c::;;;;;;;;;;
;;;;;;;;,,,,,,;:cc:;;::;::;;;;;;;:::::::::::::::::::::::::::ccccc:ccoxkOKXNNNKklc::::::::::ccccccccccclxO0K00OOKXK0K0d;,,;;;,,:;',,''',',c:',lxd:;clodxxxx0XXNNXKOdlcdK0occccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc:::::::c::::::::::::::::::::::::::::::::::::::::::;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;:;;;;;;:::::::::::::::::::::::::cccllllccccok0K00KXNWNOocc:::::::::cccccccccccccclodxxxxO0xdkxo;;;,,,',,,'',;,''',;clcl:;;ccloodk0XXX0kxdlc:;:lxdlcccccccccccccccccccccccccccccccllcccccccccccccccccccccccccccccccccccccccc::c:::::::::::::::::::::::::::::::::::::::::::::::;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;:;;;;:::::::::::::::::::::::::::::cccccccccxKNNNK0KXNXOoccccc:ccccccccccccccccccclccccccclccclddolc:,''',,;:coolcokO0KOc;::cldkOKXK0kdlccccccc:cclodoccccccccccllccccccccccccccccllcccccccccccccccccccccccccccccccccccccccccccc::::::::::::::::::::::::::::::::::::::::::::::::;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;:::::::::::::::::::::::::::::::::::::::cccoONWNX0OkOxocccccccccccccccccccccccccccccccccc:;;;;;:clol::coddxkkOOkxddxO0d:;::codxk00xolllcccccccccclxOdccccccccccllcccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc:::::::::::::::::::::::::::::::::::::::::::::::::
;;;;;;;;;;;;;;;;;;;;;;;;;::::::::::::::::::::::::::::::cc:::c:::ccccoxO00Oxdolccccccccccccccccccccccccccccccccc:;,,,,,,,,,,,:xOOOkkkxxxxxddxxo:::cccllld00dllllcccccccccccllcccccccccccccccccccccccccccccccccccccccccccccccccllccccccccccccccccccccccccccccccccccc::::::::::::::::::::::::::::::::::::::::::
;;;;;;;;;;;;:::;;;;;:::::::::::::::::::::::::::::::::::ccllc:cc:ccccccclooolccccccccccldOkoclcccccccccccccccc:;:cllcc:;;,''',:clodddlccloloooodxxxxddoox0kdolllllccccccclccccccccccccccccccccccccccccccccccccccccccccccccccclxxlccccccccccccccccccccccccccccoolccccccccc::::::::::::::::::::::::::::::::c:::
;;;;;;;:::::::::::::::::::::::::::::::::::::::::::::::::;:looollccccccccccccccccccccldkKWNkllllcccccccccclcc:;::ccccccc:;,,,,'',,;::;;:::cldk00Oxdoolllodolllllllllllllllllccccccccccccccccccccccccccccccccccccccccccccccccccllcccccccccccccccccccccccccccccoolccccccccccccccccccc:::::::::::::::::::::ldl::
;;;::::::::::::::::::::::::::::::::::::::::::::::::::cclc:clloxxdoooolcccccccccccccoxO0XWWKdllllccccccccclcccccllllccc::;;,''''''''';;;:ccllllcc::ccclllclllllllllllllllllllccccccccccccccccccccccccccccccccccccccccccccccccclccccccccccccloolllllllccccccccccccccccccccccccccccccccc:::::::::::::::::::c:::
:::::::::::::::::::::::::::::::::::::::::::::::::::cllldkdlccccllllooddlcccccc::cloxk0XNWWWOollllllcccllcclcllllllllllllllc::;,,''..',::;;;:::ccccllllllllllllllllllllllllllllcccllllcccllllllllcccccccccccccccccccclccccloolcllcccccccccccdOKK0kolllcccccccccccccccccccccccccccccccccccc:::::::::::::::::::
::::colc:::::::::::::::::::::::::::::::::::::::::cclxdd0NX0kxolodlc::lxxocccc::clodxk0XWWMW0olllllllldkxoclcllllllllllllllllllc;'...;lxdlcclllllllllllllllllllllllldkkddxollllllllllllllllllllllclllllllllllllllllllllccld00xlllllllllcc:cokXWMMNOollllccccccccccccccccccccccccccccccccccccc::::::::::::::::
:::dKXXOl:::::::::looc:::::::::::::::::::::::ccccccdOdo0NWNXOdodkkdlcloxkdl:;:clloddk0NWWMNOolllllllloxdlccclllllllllllllllc:;'...':odolllllllllllllllllllllllllllo0WW0dolllllllllllllllllllllllllllllllllllllllllllllllloxxolllllllllccclodOKNWW0olllccccccccccccccccccccccccccclllcccccccccccccc::::::::::
::cdKNNOl:::::::::oxdc:::::ccc::::::::::cccccccccccxOolk0KK0xolloddollodOKkc;::cllodx0NWMW0ollllllllllllllllllllllllllllc:;,,;cccccloollllllllllllllllllllllllllllldkkdllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllcccoxO00xllllclllllllccccccccccccccc:clok00Odlccdkdcccccccccccccccc
:::cldol:::::::::::c::::cccccccccccccccccccccccccccokdodxkkkdollllooooloxOKOo::cclodk0NWWXOkkkkxdolcccollllllllllllllccclooooollllllllllllllllllllllllllllllllllllloollllllllllllllllllllllllllllooolllllllllllllllllllllllllllllllllllllcccldxxdollllllllllllllllllllllccc:;;:coONWWKdlllolcccccccccccccccc
:::::::::::::::::::::::cclodocccccccccccccccccccccccoooxkOOkkxdooooooooodxOKkc;:ccodk0KK00KKXXK0Odc:;:lolllllllllloodxkkkkdolclllllllllllllllllllllllllllllllllllllkkllllllllllllllllllllllllllloOKklllllllllllllllllllllllllllllllllllllllllloollllllllllllllllllllllllllc:;;::cdOKXKxlllcccccccccccccccccc
cc::::::::::::::::::ccccoONWXklcccccccccccccccccccccccdk0KXXXK0kkkxddddoodkOxc;:cldO000OOOO000000kl::cdollllloodxk0K0Oxdolllllllllloxkkollllllllllllllllllllllllol:dOdloloollllllllodolllllllllloxkdlllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllc:;;:::coxxolcccccccccccccccccccc
ccc:::::::::::cccccccccco0NNXklcccccccccccccccclccllccd0XNWWWWNXKKOkkxxxddxkdc;:lxkkkkkkkxxxxxxkkkoccxkoloodk0KKK0kdolllllllllllllloxOkollllllllllc::cllodollollol:cO0dooooooollllc:dkololllllllllllllllllllllllllllllllllllllllllllllloddollllllllllllllllllllllllllllllccc:;;;;::cllllcccccccccccccccccccc
ccccc::::::cccccccccccccclodolccccccccccc:::cccccllllox0NNWMWWNOdddok0kdkOkkdoooxkkxxdddddddddxkOkdllk0kxOKXXKOxdollllllloolllllllllooollllllllllc;'''',:lxkdooool::kX0dooooooolc;;,lkdlolllllllllllllllllllllllllllllllllllllllllllllloddollllllllllllllllllllllllcc:::::;::;;;;cccllllllllllcccccccccccccc
ccccccc::cccccccccccccccccccccccccccccccc:;:collloddoooxKWN0kxkd:colokl:d00xldOkdooddddddddodkO0OxolldOKKKKOkdolcc:;;;;:ccooolllollllllllllllllolllc;,,'',:x0koooc::dXN0doooolc;,,;,cOxoooooooooolllolooollllllllllollllllooooolllllllllllolllllllllllllllllllllc:;;;;;;;,,,;;::cllllllllllllllllccccccccccc
cccccccccccccccccccccccccccccccccccccccccclkKX0O00KKKOddx0kc,,cl:,;;:l:,:dOkddkd;,;lddoodooodxkkkxolodxddoooddoc;,,,;;;::clxkdololllllllllooooooooooolc:,',,l00xoc:cd0XNOdol:;;,;;,,ckkoooooooooooooooooolooooooooooooolloodkkkxoooooooooollllooooooollllllllll:;,,,,,,,,,;:cllolllllllllllllllllccccccccccc
cccc:cccccccccccccccccccccccccccccccccccclkXWWWWWWWWX0xdlc:,,,',;:;','';c:looxOd;,,,cxxooodddddxxdooodlcccclll:;;;;;;;::ccoxxdoooooooollloooooooooooooolc,,,,cOKd::cdOOKOo:;;;,;;;;;:x0xoooooooooooooldxooooooooooooollclookKNNX0dooooooooooooooooooooooollollc:;;;;;;;;:ccllllllllllllllllllllllllccccccccc
cccllcccccccccccccccccccccccccccccccclc:cld0XNWWWWNKOdol:;;,,,'',',,;::;::olokkoc:,,;ccloddddddddooodo:;::::;;;;;;;;;;;::looolloooooooooooooooooooooooool:,,,,:kkcclk0xoc;;;;;;;;;;:cxX0oooooooooolc;;cooooooooooooool:;:ccoOXWWXkooooooooooooooooooooooooooolccc::::ccllllllllllllllllllllllllllllllccccccc
cccolccccccccccccccccccccccccccccccccc::ccoxOKNWWNKkdolc;;,,,'',,,;;,cc;;clc:c:;cl;',,;looooxOxdoodddc,,;;;,;,;;;;;;;;:cloooooooooooooooooooooooooooooool:;;;,'ckdldkkc;;;;;;;;;;;;;:dKKkxxxxolcc;,,;coooooooooooooooc:;;;;:lxO00xoooooooooddddddddddooooooooddxxxxxdooloodxdlllllllllllllllllllllllllllllcc
ccccccccccccccccccccccccccccccccccccc:;:ldkKKXNNNKOxolll:,'',,'.'',;,:c;,,,:lccooo:,,:lolc::o00xodddl,,,,,,,;,;,,;;:cloooooooooooooooooooooooooooooooooooc;;,,''cdlc:;,,;;;;;;;;;;::cONX0Oxdl:;,,,,;loooooooooooooooolc;;;;::coddooooooooxO0OOOkkxxxdollccllodxkOKXNXKOdooxxdollllllllllllllllllllllllllllll
cccccccccccccccccccccccccccccccclccccccccoONWWWWWNXOdlcc;,..''',,...,,';l:,:ol:odc,',;::ccc:oKXkoddc,,,,,;,,,;;:cclooooooooooooooooooooooooooooooooooooooc;;,,'.,;,'''',,,:cc::;;;;;o00ddl:;;,,,;;:ldooooooooooooooooollcclllooooooooooodOKKOkxdoool:::::cclldxk0XWMMMWKkoooooooolllllllllllllllllllllllllll
ccccccccccccccccccccccccccccoolcllc:::cccoONWWWMMWN0xl::;,.,;,''..'',,'',,'',,,,,,'',c:;:ccoOXK000x:,,,,;;:cclooooooooooooooooooooooooooooooooooooooooooo:,,,,'.''''..',,,:lc:::;;;codc:;;;;,,;:coxxxdddkkxdoooooooooooooooooooooooooooodxxxddoooolc;;:::ccclodxOKWWMMMWXkoooooooooollllllllllllllllllllllll
cccccclcccccclddlccccccccccclllcoxxlccccokXWWWWMWNXOxoc:;,',;,';;,;'....'''''',c:''''',;::lx000KKOl,,;;:cldddoooooooooooooooooooooooooooooooooooooooooool;'',,...'''...',,;;;;;,,,;ll::;;;::ccclooollc::ldkOxddoooooooooooooooooooooooooooooooooool::::::cccccloxOKNWWWWN0dooooooooooooollllllllllllllllllll
cccccccccccclkXXklccllllllccldxxdxdlllllldOXWWMWWNK0kdl:codl;,,;;,''',,''';,''',,,;:,',::lxkxxkkxl;;;;;:::clooxkxdoooooooooooooooooooooooooooooooooooddo:'';;'...''....''',,,,,,,';lc;;:::c::::::cllllccc::dkddddddoooooooooooooooooooooooooooooool::cccccccccclloxO0KXXKOxooooooooooooooooollllllllllllllll
ccclooollllcldOOdllllllllllldOK0dllllllllllox0XNNNXKOxdllx0N0o;'',;,',,'''''';:,',;:,,;:lxxdoodoc:::ccccclloddkKNXOxdooooooooooooooooooooddddddddddddooc,.,:;,'.........'''''''''':c;;:::;;;;;:clooodddddl;:odddddddoooooooooooooooooooooooooooooolc:ccccccccccccclldxkkOkdooooodO0Oxooooooooollllllllllllll
lcoOXXKkolllllllc;;cllllldO0K0xollllllllllollllodk0KK0kxlco0XXk:',;;,,,,;c:,,:c;',,',;:lxkxolllcccllloooddxxkkk0XNKkdoooooooooooooooooddddddddddddddoc;,'';;,'...........'''''''',,;:::;;;;;:clodddddddddooodddddddddddddddddddddddooooooooooodddoollllccccccccc:ccclooddddddooox0KKxooooooooooooloollllllll
lldXNNNKdllllllc;',;:clld0NNNNOollllllllllolloollllodddocc:cdkkx:,,,,,;;;c:,,;,,'',,;ldkkkdc:::looooodxxkOOOO000Okdoooooooooooddddddddddddddddddddol;'''',;;'....''.......'''''',,,;;;;;;;:cloddddddddddddddddddddddddddddddddddddddddodddodddddddooooolcc::::::::::coxOOkOOOkdodxkxddxkxxdooooooooooolloool
llok00Oxlllllll:'',;;:cldOXXXKxolllllllooloooooooooooooooolc::oxdlc;;;;;,,,,,,,;:cldxOOkxo:,;cloddxxxkkkkO0000Okddddddddooooddddxxxxxdddddddddddoc:,'..',,,'.''''''''...''''',,,,,,;;;;:::cloddddddddddddddddddddddddddddddddddddddddddddddddddddk000kdoloo:::::;:clookKKK0KKOxooddddxkkkkkxdddddddddooooooo
llllllllllllllc,''',;;:cllxkxooollllooooooooooxdoooooooooooc,';cdxxdool;,,,,,,,;:clooooooolcccccllodxxkOOOOkxdddddddddxxxxxddddddooolllccccccc:::;;,,'''''...'''''''''''''',,,,;;;;;:::cccloxkxxxxxxddddddddddddddddddddddddddddddddddddddddddddOXNNNXOxdoolcc:;,,:codkOOOOOkxddddxddxkkkkOkkkxxxkkkkkxdoooo
oooooooooooool;''''',;,;:clxOxoooooooooooooooooooooooooooo:....;cldxxdolcc::;::::clooddddddddddoooooodddddddddddxxxddddoollcccccc::ccc:::::::::::::::;;;,,,,,,''''''',,,,,,,,,;;;::::ccclldkkkkkxxxkxxxdddddddddddddddddddddddddxxddxxxxxxxxxxxxOXNNNNK00OkOOxdlcllodk0XXXKkxxxxxxxxxxxkOO000OOkkOOOOOkxdddd
xxdddddddddddl,'''''',,,,;:cdkxddddxxxxxxxxxddddoddddddol,...':oddddxKXXK0OxddodkO00Okxxxddddddddddddddddddddooooolccccccccclolccccc::::::::ccccccccc::::::::::;;;;;;;;;;::cc:::::::ccclloxkkkkkkkOOO0OkxxxxddxxxxxxxdddddddddxxxxxxkkkOOkkkkxxxxO00KK00000K0O0KKXXKKKXWWWN0OOkkkOOOkkOOO00K00OkkOO00OOkxxxx
kkkkkxxxxxxkko,''''''',,,,;;:oxkxxkkkkOOOOkkkkkkxxxxxddc'..',oxxdddl:oOXWWNNX00KNNXX0kkkddddddddddddddddollcc::ccccc::ccccc:loc:::::::::cc:::::cccccc::cc:::::cccccccc::cccllloxxxxxxddoodxkkkkkOO0KKXXK0OkkxxxkkkkkkxxxdddddddxOKK0OOO0OOOkkkkxkkkkkO0KKK00O0KNNNNXXXNNWNXK00OOOOO00OO000000OOOOOOOOOOkkkkO
kOkkkkxxxxkkkd;'''''''','',,;:ldkOkOOOO0KK000000OOOOkd;...':dkxxxdxxo:cdKNWWWNNWWNXK0Okxdddddddddddddollc:::::::::::::::;::;::::::ccc:::::::::ccccccccccccccccccccccccccccccccldk0XNNNX0kxkkkkkkOO00KKKKOOkkkkkkkkkkkkxxdddddookXWWN0OO00OOOOOO0KXX0kk0KXK0OkkkO000KKKKKKK0000OOO0000000K000OOOOO0OOOkkOOOOO
xxxxxddddddxxdc,',,,''''''',,,;:x000OO0KNNNNXXXXKK0kl,.'',cooolccccloolclx0KKXNWWNX0Okxxxxxxxxxxxxolllodl::;;;;;;;;;;;::::::ccc:::ccc:::::::::cccllclodxkxolllllccccllcccccccllodkKNNWWX0kxxkOOOOkkkOOOkkkkkkxxxxxkkkkxxxxddooox0XXKOOOOOOOO000XNWWX0O0KKK0OkkkkkkkkkkkkOOOOOOO0000OOOO000OOOOOO00OOkxkOO00O
xxddoooooooooooc,',,,''''''',,,;o0KKXXXNNNK0OKWWWNk:''''',,,''....'',;:clldxdd0X0OkkkkkkkkOOOOOdoodddoc:,,,,,,;;;;cc;:cc::::::::::c:::::cccclllllooodddxOOOkkxdollllccccccclllloddxkkOkkxdddddxkkOOOOkxxxxxkkkxxxxxxkkkxxxxxxxxxk0KXXX0OkkO00000KNNXK000000OOO00OkkkkkkkkOOOOO000000OOOOOkkkkkkkkkkkxddxkkkx
xxxdddooooooooooc,''',,''''''',,:kKKXKOkdl:::oKW0o;''''.........''''''',:oxkOxOOkxkkOOOOO0KK0xodk00kl;,,,;c:;;;;;;;;:col:::::::::cdoc:cccllollooddxxxxkkk0XXX0kxddolllllcclllllooooooooooooooodddxxkOOOkkxxkOOOkxxkkkkxxxxxkOOOO00XNNNXOxk0XKOkkO0KK0OO00000KXXXK00OOOkkkOOOOOO000K000OOOkkkOOOOOOOOkxdddddd
dddxxxxddddddddddl;'''',,,,'''',;oO0kc;,,,,,,;ld:',''.........''''''''',cxkkkkkkkkkkOkkOKK0xllxO0ko;,,,,,;lc;;;;;;;;:okd::::cc::::cc::cccclloddddddxxO000KNWNK0OkxdooooollllllllllooolllllooooodddddxxkO0OO000OkxkkkkkkxxxxxkkOOOO0KKK0OOkONWXOkxxxxkkkOOOOO0XXXXXK00000OO0000OOO0KK00OOkkkkO000O0KKKOdoddoo
dodxxkkkkxxxdxkOOOkl;,;coxkkxoc;;lOx:',,',,',;:,'''...........'''''''',ck0OOOkkkkkkkkkkOOxl:cooc;,''''',,,,,;;;;;;;;;:::::;:lc:::::::::::ccclodxdoodxO00KNWNKKKOxxddddoolllollooolooollllloooooooodddddxxk0KX0kxxkkOOOOOO0K0kxkkkxxxkkOOOxd0WWNKOxxxxkkkkkkOO0KXXXKKKXKK00000000OO00OkxxxxxxxxkkkO0KKOxddooo
dddxxkkOkxxxlccllooc;,;;;cldk0KKkxkd::;,',''';;''..........'''''',',,;lkkkkOkkkkkkkkxxxoc;,,,,'..''''',,,,,,,;;;;;,,;;;;::;;;;;;:::::::::::cccllloodx0KXXWWX0Okxxddddddoodooloodddxxdolllloodxxddddddxxxdxxk0KK0OkkOO0O0XNWN0xxxkOOOkkOOkooxXWWNX0kkkkkkkxkkk0XXK00KNNXK0OOkOOOOOkkkxddddddddddddxxO0Oxdddoo
xkkxxkkkxkOko:,,,::;,,,'',,,;:oxOOxddxdoc;'''''.........'''''''',,',:oxxddxxxxxxdddddoc;,'',,'..',,''',,;:,,,,,,,,,,,;;;;;;,;;;;::;;;;:::::::cccllooxkOOKXXK0OkxdxkxddooooooooodxkkkxdooooooxKX0xddddxkxddxxkOKXXK00KK00KNNN0kxO0KKKK0K0dlod0NMWWX0Okxxxxxxx0NNNNXXNNNXXKKOkxxkxxxxxddddddddddddddxKNNXOdooo
OOOkkkxdlllc;,,,,;;,'''.'''',,',;::okOkkxo:,'........'''''''''''',:ldxxkkkxdddxddddoc:,'',,,'..',;,''''',,,,,,,',,,,,,,,,,,;;;;;;;;;;;;:::::::cclloodxxxOKK0OkxddxkxddooddoodddddxOkxdxxxdodxkkkxkxdoddddxxdxkkOKNNNNNXK000OkkO0KKXXKK0xooooxKWMMWNXKOxxxxxxOKXXNWWWXKKKXKKOkkxxxxxxxxxxxxxxxxxxddkXWWN0dooo
000OOkkl;;;;,,,,,''''......',,','.'l0NNXKOd:'.........'''''''',;codddOXNNXOdddddddl:;,'',,'...''''''''''''''''''''',,,,,,,,,;:ol::c::;;;;clc:::ccllodddxO00OkxdddddooddxO000KXK0OOOkxxxxxdddxxdddddddddddddxxxxkk0XNNNXXXK0OO00KKKKKK0xolllookXWMMWWNXKKK0OkO00KKXXK0OO00000OOOO0Okkk0KXK0OkOKKKOxxk00Oxdddd
00OOOOxl;;;,,,,''''';;''......','..,l0NWNXko;.........''''',;cldxxdddkKXNKkddddddl:;,..''....''';,''''''''''''''''',,,,,,,,,,:ooclllc:::::cc:::ccclodxkkkkkxxdoddxkO0KXNWWWWMMMWWNKOkkxxxkkkxxxxddxddxxxddxxxxxxxkOKXNNXKKK00KKXXXKK0kolllllodONMMMMWNXNWNK0O0KK0OkkOOOkOOOOOO0KKK00KNNNNX0OKNWWNKK0OOOkkxdd
Okkkkkxc;;;,,,,,,'..,,....'..........c0WWXOo:'...'',,;;::ccodddxOOxdddxkkxdddddoc;,'..''....''';:,''''''''''''''',,';;,,,,;cldxkkxdoc::::c:::::ccoOXXXXXKKK0000KXXNNWWWWWWWWMMMMMWWX0OOOkO0OkkkkkkkxxxOOkxkkkkkkOkkO0KXNXKKKKKKXKK00OdllllllloxXWWWWWXKNWWNX0KKK0OkkkOOkOOOOOOO000OO0XXXX0OO0XWWWWWNXXX0kxxx
xxxxxxxl;;;;;;;,'......'.............'oKN0xl:,.':oddxxdxxxddddxxkkxddxxxxxdxxxdc;,,..,,'....',,''''....'''',,'''',:;;:,,;cdxkkOOKXXKOdlc:c::::::cd0NWWWWWWWNNNNNNNNNNWWWWWWWWMMMMMMWX0OOO000000OO000OOOOO000OOOO0K00000KXX00KKKK0OOOxlllccccccoONNNNXK0KNNNXXXXK0OkkkkkkkOOOOkkkO0KKK0OOOkkxkOKXNNXK0KK0kxxk
xxxxxxxxl:::::;'..........';'........';cdkdc:;coxxxkkkxkkkkxxkkOOOkkkOKK0Okkkxc;;,'';,'.....','';,....'',,,,''''''''''';ldxxxxkkO0KXNNXklc::::;;:dxOXNWNNNNNNNXXXXXNNNNNNWWWWWWWWMMWX00KXNNNNXXKKXXKK0KKXNNXK0O0KNNNKKKO0KKK00K0Okkxo:cccc::::cxOO0KKK00XNXXXXK0OOOkxxxxkO00Okkkk0NNNKOkkxxxxxxkkkkxkOOkkkkk
kkkkkxoc;;:c::,..,,'...........'........':llc:::coxxxxxkkOOOOOOO00K00KXXXK0OOd:;,',:;'.......'.';,..'',,,,''''''''''''';dddddxxxkO0KKNWWKxl::;;,;oddk0XXNNNXXXXXKKKKKXXXNNNXXKKKXXXKOkOKNWMMWMWWWWWWNNNWWMMWNXKXXNWNXKKKOOKKKKXNNKOxl::::::::::okxkO000000OO00OOO0OkxdxxkkOOOkkkk0XNXOkkxxddddddxdx0XXKOxkkk
O00Okdc;,,,;;,,'.'......'..,........'.....':l:,,;lkkxk0K00KK00000O00O0KXXK00kl;,',:;''...''....','.',,,,''''''''''''''',lddooddxxkkO0KNWWXkl:;;,':ooddxkKXXKXXKKKKKKK0OOkxdoooooodxxdxkOKNWMMMMMMMMMMMMMMMMMMWWWWWWWWXX0kOKXXKKNWWNkc::::;;;;;:oddxkO00OOkxxkkxkkkkxxxxxxxxxxxxxxk00OkxxxxxdddddddxKNNXKKXKO
OKX0kdc;,,,,,,,'..';,....','................,;;coOOxx0XNX0000O0K0kxxkkOkkkOkc;,,;cl:,'...''..''...',,,'''''''''',,'''''';oollooddddxkO0XWWKo:;;,,',cloodxkO00000Okxdolc:::coodddddddddxkk0XWMMMMMMMMMMMMMMMMMMWWWWWWWNK0kk0KKK00NWXo:::;;;;;;;:loodkkOOOkxxxxxxxxxxxxxxxxxxddxxxxxkxxkOOxxxxxxxxxdxkOOOXWWWX
dkkxxd:,,,,,,,'.''...,'....;;.',.......''...':loddxxxxkO0X0Okkkkxxdxxxxxdxxl;,,:odl:,'...........',,,''::'''''',,''''''..;lllllooooddxk0XNXx:;;,,,'',;::cloodxdlc;;;:ldkO0KXXNNNXKkxxxxxkk0KNWMMMMMMMMMMMMMMMMWNXNWWNXNNKOkk0KK00XOc::;;;;;;;;:loldxxkkkkxxxxxxxxxxxxxxxxxxxddddxxxxx0NXOxdxxxxxxxddddxOKXX0
ooooo:''',,,,'............,'...............'::;:loddddddk0Oxxxxddddddddddxl;,,;lxdc,,;,'........',,,''';,''''',''''''.....:llccllllloodkOKXx:;;,,,,,,''',cddc:;;coxkOKKKKKKKXXXXNWNXOxxxxkkkOKXWWMMMMMMMMMMMMMWNKKXKXXNWWX0OOKK0OOdc::::;;;;;;:cllodxxkxxxxxxxxxxxxxxxxxxxxxdxxxxxxdxxkkxdddddddddddddddxxxx
ooool;''''',,'............''.......''.....';;;;:clddddddddddddddddddddxkxo:,,,cooc;';:;,.......',,''''''''',,,'',;,.......'clcccccccclllokOl;;,,,,,;;:ccldxdoodxkOOOkkkkkkO000KKKXNWXkdxxxkOOOO0KXNWWWWNWWWWMWNK000KXWWMWWX0k0K0Okolcccc::;;;;:lllodxxddxxxxxddddddddxkOOOOOOOkdxddddddddddddddddddddddddddd
oll:,,:;'''',,'............'.............,::;;;:coddddddddddddddddddddxkxc;,,;coc;'',;,'..'...',,''',,'''',,,'',cd:.','.',;c:;;,,;;::cclloc,,,,,,,;:ldxxxxxkkkkxxdddolc::lxkOO0000XNNOdddxOKXK0OkOOOOOOOO00KXNNK0kk0XWMMWWWX0O00Okdlcc::::;;;;:cclooooodxxdoolllooooddxkkxddk0kxxddddxdddddddddddddddddddddd
:;,'..,c:,,'''.................'.......':cc;;;;:::coddddddddddddddddddddo;,,,;cc;'''''...',..',,'''',,,,,,'''''',;,...',;;,'...',,,''',,,,,,,,,,';ldddxxddddxxdolc:;,,'';oxxkkOOOO0K0xoooodxkOkkkxxxdddddxxxxkKXKkxkOXWWWWWWXOkkOkdlcc::;;;;;:cllloloooooollllllllllooddolcldxxxxxxddxddddddxddddddddddddddd
,,'....';:;,,,'..........'...........';ccc:::::;'',:loddddddddddddddddxdc;,,,,;;'.','........''''',,,,,,,''''''''.''.'','''',:lodxkkxl;,,,,,,,,,':dddddddddddl:;,,'''';ldxxxxkOO0OOkdollllooooodddddoooooooooodkOkdodkKWWWWWN0kkOOxoccc::;;;;:llloooooolllcccccccclllcccc::oxxxxxxxxxxxxxxxxxkxxxxxxxxkkkkO0
.....,;:llc:;;,,,'............'.....;cc:::::;,'.'',;clddddddddddddddddxo:;,,,,,,'.';'..'...'''',,,,,,,,,,'''''''''';,'''',:loddddxk0XX0dc;,,,,,'',cooooddddd:,,,,,,,:ldxxxkkkOOOkdlcclc:cccccllloooooolllllllloooxxdddkXWWWWWX0kkOkdlcc::;;;::llllllllllcccccccccc:::::::cldxxkkkxxxxxkO00OkxkkkkxkkOO00OKNW
.';:loooooolc::;,,........'',,'......,;,,,''..',,,;;clxkxddddddddddddddl:;,,,,,,'....','..'',',,,,,,',,,'''''''''':o:';:loddoooddddxk0XXOc,,,,,;;,,:loooddl:,,,,;:codxxxkkkkOOxoc:;:::::::::ccccccllllccllcclllllodoood0WWWWWWXOkOkdl::::;;;:clllcccccccccccc::::;;;::::cokkkOKKKOkkkkk0K0OOOO0000KXK0kkkOKK
cloooooooooooool:,''''...............''.....',,,;:::cldxxddddddddddddddl:;,;:;;;'...',,...',,'',,,,''''''''''''''':lllodoooooxOOxdooodx00l,,,;cdx:',cloodxc,,,;codxdxxxxkkOKKOo:::::::::::::::::::ccccccclccccllcloolodkXWWWWNX0OOkxo::::;;;:llccc::::ccccc:::;;:::::::lx00000XNNK0000O000OOKKKKXXXXX0kxxdxx
ooooooooooooooooc;;;,,,,,,'''''....','';c:,'',,;;::cldxdoodddddddddddddol:;;c:,,'...'''..'',,,',,,,,'''''',,;;;:cloooooooooooxOOdooooodxd:,;ldxdo;'',:cldxdlloddddddxxxxxkOKXNXxc:::::::;:cc:::c:::::ccccccccccccllollodk0NNXXKOkOOkxdc:::;;ccc::ccccc::::;;:;;;:::::lx0KXXK0000000000OkkkxxkO000KKKXX0Okxxx
ooooooooooooooooc;;;;;:::;;;:;;,,,,''..,ldolc:;,;;;:coxdoodddddddddddddol:;,,,,,'........',,,,',,',,''''';odoodddooooooolloooooooooooodl::ldddoc;,,''',;loddddddddxxxxxxxkkkO0XOl;::::::;;;;;;;::::::cc:::::::ccclolllloddO000OkxOOkkOkc::;:ccccccc::;;;;;;;::;:::cokKNXKKKK0OkxddddolccccccclodxO0KK00OOOkk
oooooooooooooooooc:;;:::ccllcc:;;,'..'''cdddddolcccccloodddddddddddddddo:;;,,,,'''....''.';;,'',,,,''''',ldoolooooolloollllllllooooodkkoodddol:,,,,,',;:ooodddddddddolclllodk0Kkc::::::::;:::;;:;:c:;cc::::::::cclllllloodxO00kxxOOOkkOxl:;:lcc::;;;;;;;:clooc:clox0XXKKK00kdollcccccccc:cccccccoO0000OO00OO
oooooooooooooooooooc;;clllll:,,',,,'',,;coddddddddddddddddddddddddddddxoc;;,,,',:;'......,;:;'',,''''''.,llccccloollllllloolllloooooodxddoool;,,,,,;ldddooodddoolc:;,,'''',:oOKOxxxxdoolc:::::::;:c:;::::::::::cccccclllodxkOOkxk00OOkkkko:cc:;;;;;:cllldk00OdooxxkO000000klcccccccccccccc::::cok00O0OOO00OO
ooooooooooooooooooooc:cllcll,.'',:;;;:cldxddddddddddddddddddddddddddddoc::;;,''',,,''....''''''''''''''..;cccccllllolllllllllllllooooooooooc,,,,,;oxdooodddoc:;,,,',,,;:cldkO0KKKKKKKKKK0kl:::::;;;;;;;;::::::::cccccllcloodkkxxk00Okkkxdl:cc:::cldOK0kxxooollooodxkOOOO00kddxkOkkkkkxoc:cc::cdkkOkkkkkkOOOO
oooooooooooooooooooodooooooo:,,;;:c:codkOxdddddddddddddddddddddddddddxdl::;;,,''..'',,'...,,'''''''''''...,:ccccccclllllcclllllllooooooool:,,,,,cdxdoddolc;,'',,:coddxkkOOOkkkOkkkkkkO0KXXKdc:::;;;;;;;;::::::::ccccllccllodkxxkOKKOkkxo:;;:lloxkkkkxoodocclcccloddxk00O0XKOkkOOkkkkO0K0koccldxxxxxddxxxxxxx
ooooooooooooooooooooooooooool:,;;:lloxOX0dddxkxddddddddddddxkxddddddxOOo::;;,,''....',,'..,,'''''''''''''..',;;::::::::;',cllloooodoodddl;,,,,;lddoolcc;'',:ccoxk00KKK0OkkxxxddxkkOOO00K00XXxc:::;;;;;;::::::::::cllllccllodddxkO00Okdccllc:loxkkxolloolc:cccc:clodk0XNX0KX0kkxxxxxxxk0XX0oodxxxxxxdddddddxK
oooooooooooooooooooooooooooool:;;:lodkOOxddxOKOddddddddddddddddddoodKWWOc::;,,,''''.'''''....'''''''''''........'''''...';lllooooooodddl;',,,:oddddl,,;;:loxxxxdxkOO0Okxoc:;;;;;:lxO0KKXX00KKd::::;;;;;:c:::::::::ccc:clllodddddxkOOkdoc:clxkOkkxolollc::::::::::coxOKNNKxx0OkxxxxxxxxkOKXOxxxxxxxxxddddddxO
ooooooooooooooooooooooooooooodol:;codOOxdddddxdddddddddddddddddddollxKN0l::;;;,,'''''''''.......''''.....'''.''''''''.';clllloooooooxxo;',,,:oddx0xllooodddolloooxkO00d;,,,;;;,,',;cxOKXXXK0KOl:::;;;;;cc;::;;::::clc:lolldddkkdxkOOkkkkxoccdxdlcloolc:::::c:::::ccldkO00xox0KOxxxxxxxxkO0kxxxxxxxxxdddddddd
ooooooooooooooooooooooooooooodddocccldddddddddddddddddddddddk0Oddoolodxdc:::;;,,,'''',,''....'''''......''''''''''.';:clllllllllooodkd;,,,':oddxKXOdoooolc:;,.,lodxk00o;;;;:ccc:,,',cdkKXXXKKKd::;;;;;;;;;cc;;;:::::::llllddxxddkOkxkkkkkkkdldkdclddolc:cccc:::::::clodxdddxOKOxxxxxxkO0K0kxxxxxxxxddddddddd
ooooooooooooooooooooooooodddooooooolloddddddddddddddddddddddk0Odddddxxxdc:::;;;,,,,,,,,''.......''.......','''''',;clollolllloollloxx:,,,';loodxOkdoccc:;,'''''coddxOKx:;;:clddl:,',:lokKKKK0Kkc::;;;;;;;;::;;;:::cc:ccccodkxddkOOkxkkkkkk0KOdxOdcokkoccclllcccccccccc:;;;coxOkxxxxxxkkOOkxxxxxxxxxddddddddd
ooooodddoooooooooodddoooodddooodddddx0Kkddddddddddddddddddddddddddddddxdo::::;;;,,,,,,,''........''''...',,'''';coollllloooooooooooxd;,,,,coloddddoc,,,,,,,,,',coddxOKXOkxxdddoc:;,,coodkO00OKOc::;;;;;;;;;;;;;:;:cc:cclldkxookOOkxkOOkkkkO0Okdol:;::;;:d0K0kddooodxxdolc;clcokkkkxxxxkkkxxxxxxxxxxxdddddddd
ooooodxdoddooooooodxdooooooooodddododO0kdddddddddddddddddooddddddddddddxkd::;;;;,,,,,,'''..........'....,,'.',cllllllllllllllllllookd,,,',colloodddc,,,,,,,,,;loodxxkkO000KKK0kl;;,;lodxkOOOOKOl::;;;;;;;;;;;;;;cc:::ccodoolodkOkxxkOOkOKXXXK0Oko;,,:lc:lkXXKOxolloxkOO00dxkdxOOOOOkkkkkkkxxxxxxxxxxxxdddddd
ooooooooodxdoooooooooooooooooooodoododdoddddddddddddddddodk0kddddddddxddkOo:;;;;;,,,,'''.....,,'.'''...''''.,clcccllllolllcclllllookd,,,''cllloodxxl;;,;:cllodddodxxxxxxxxkk0K0o;,,cdddxOOOkk0xc:;;;;;;;;;;;;;;;:c:::cldkxlldxxxxxxkkkk0NWWMWN0Oxc;,:oxkkdkKXKkdolloxxxkO0OkkOKKK0KKKK000OOOOkkxxxxddxxddddd
oooooooooodooooooooooooooooooooodoooddddddddddddxOkdddddk00Okddddddddddookxc;;;;;;''''''....',,'......''''..,lllccccclolcccccllllodkd;,,'';lllooddxxlcllodddooooooddxkxoclodk0xc,,:dkkxxkOOkkko::;;;;;;;;;;;;;;;;;::::clxxoldxxxxxkkkkkk0KXNNKkxo:;;;cllc:cxO0OkdollddoodkOOO0KXXXXXXXXXXXXXK0Okxxxxxxxxdddd
ooooooooooooooooooooooooooooooooooooddddddddodddOXKxdddodxdddddddddddddddxxo:;;,;;,'''''...........,,.'''...,clccccccclllclclllllllxd;,,,',cllloodk0Oxxocc:;;,,:loodxko;,;cooc;,,:dkO0OkkkkkOd:;:;;;;;;;;;;;;;;;;;::::clxkdooxkxxkkkkkkkkkkOOOxol::;;:oxdc:cldxxddooooooodk0KKK000OOOOOO00KXXXX0kxxxxxxxdddd
oooooooooooooooooooooooooooooooodddddddoddddooooodxdoooooddddddddddddddddxxoc:;,,;,'...............''.......';cccccccccccll::cclllldx:,,,'':llooooxkl;;,,,,,,'';lodxOkc;c;;;;;;;:dOK000OkkkOxc::::;;;;;;;;;;;;;;;:;:::ldxdoodxxxxkkkkkkkkkxdddolcc:::;lkkkxololooddxxxxdodxxxkkkkkkkO00OOOOOOO0OOkxxxxxxxddd
oooooooooooooooodxdooooooooooooodddddodddddoddoooddoolllodooodddddxxxdddddddoo:,,,'...............','........';:c:::cccll:'.,:ccllloxl,,,'.,:loddddkd;,,,,,''.':oodxOx:;:;;;;;;cx0KKKKKOOkOkl::::c::c:;;;;;;;;;;:::::clooolodxxxkkkkkkkkkkdl::cccc::c:lOKOkkkkxloxkdlloodOOkooodddddxxxxkkkkxxxdxxxxxxxxdddd
ooooooooooooooooOXKxooooooooooooddddoooodddddoooooollllokkddxxxxdxxkxxdddddxxxl;;,'..''............''.''......,;::::cllc,''.':clllooxd;,,''.;cloddoxkl,,,,,''';loodxOo:;;;;:::lx0000K00OOOko:::::llcc:;;;;;;;;;;::::::ccccloxOkkkkkkkkkkkkxololcc:::cclkX0kkkkOxloOOdcccoxOOOkxlccccclooxOOkxxxxxxxxxxxxxddd
oooooooooooool::d00xoooooooooddddddddood0Kxdolc::;:lolclxkxxk0KKOxddxxxxxxdxxkdc;,,'..''.............','.'......',;;;:;'''..':clllllxkc,,,''';cloodxOkdl::::cloddxkO0d:ccclodxO0000OO0OOOxl::::::::::;;;::;;::;;:::::::::cloxOOkkkkkkkkkkkkxxxdc:::::c:lkkkkkOXNOookxl::::lxOOkxdoooooodxkO0Okxxxxxxxxxxxddd
oooooooooooooc;,;cloooooooodddk0KOxdddk0X0dol::;;;;:c:cldxkO0KK00kxxxkOkxdxdk0Oo:,,''.',...........'',''''''.''''''''''''''.':cccllldOd;,;,'.':cllodxOOkxxxxxxxkO0KXNK000KKXK0000OOOOOOkdc::::ccokOdc:;;cl:;;;;:;;;;;::::cclkOxook0Okkkkxxxkkkxl::::::cokkkkkkOKKdcllc:;;;cdkkkkkkxxxxxxxxkkkkxxxxxxxxxxxddd
:ooooooooooooolcllooooooooooooxKWNOdddxKXkoc::::;,;;::clook0K0O0KOxdddxdddddxxxdoc,''........''.....''''',,,,,,,,,,,,,,,,,''';ccclllokkc,,,'''':cllooooooodddddxkk0KNNWWWWNNXKKK00OOOOkocccccccoOX0dc::;::::;;;c:;::ccccllldoc;;;lOXKkdodxkkOOOxo:::::oxkkkkkOKX0xolldo:;;okkxkkkkxxxxxxxxxxxxxxxxxxxxxxxxdd
,:loooooooooooooooooooooooooc::oxkddooodxdoc::::;;;;;::clldkkkO0Oxdddxkkxddxxxxxddc,'................'',,,,,,,,'''',,;,,,,,,',:ccccloxOl,;,,,''';clllooooooooooooodxkO00KXXXXXXXK0OOkdc:::::::::lol::::::loc;;:ccclllllllodl;'':::cdOxllodkOKXXX0xlcldxkkkkkkk0K0kkxdxxl;cdkkkkkkkkkkkxxxxxxxxxxxxxxxxxxxddx
;;:looooooooloddoooooooooooollllooooooooool:::::;:::::coddoooooddddddxO0OxxkOkkkkOko:,.';;..'....','...'',,'..'''.'',,,,,,,;;',:cccclxkc;;;;;,,'',;:cccccc:::::cccclooodxkkO0KK00Okdl:;;;;;;;;;;;;;;::cxOko:::clolllllllloc,..',;,,;:c::clodOXWWWXOxxkkkkxkkkkkkkkkkkxdoldkkkkkkkkkkxxxxxxxxxxxxxxxxxxxddddk
cclloooooddollodoooooooooooodkO0OkOkxddoooc;;:c::;;;;;:cc:;,,,,:coxxxxk00OO00KKKXXXX0o;'''.'''''.','...''''........'''''''',,,,,;::cclc;::;;;;;;;;,,,,,,,,,,,,,,,,,;:cllooddxkkkxoc:::::::::::;;;;;;::lkK0o:cclllllllllllo:;:;'',,,;;;;;:::clxOKXNX0kkkxxxxkkkkkkkkkkkkxxkkkkxxxkkkkkkkxxxxxxkkxxxxxxxdddolo
ooooooooooooooooooooooooooolloxxxxOKXK0Odl:,,;;:ll::ccc:;,,,,,'',;cxO00KXXNWWWWWWWNXX0xc'...............''.......,'......''',,,,,,,,,,,;;;,;;;;;;;;;;;;,,,,,,,,,,;;;;;:cccloddol:::::::::::::;;;;;;;;;::c::cllllllllllllodxkOxl:,'',,,;;::::ccodkOOO0Okxxxxxkkkkkkxxkkkxxxxxxxxxxkkkkkxxxxxxxxxxxxxxxxdddddd
ooooooollooooodddooodoodooollcccccloddxkxc'':l::do:lool:;,''',,,,,,:xXWNNNXXXKKKXXK000Odc;'......................'''''..''',,;,,,,,,,,,,,,,,,;;;;;;;;;:;,;;;;,;;:c::::;;:::::::::::::::;;;;;;;;;;;;;;;;;;:clllclcllllooodkOOxxxdc;;;;;;::::::ccllood0Oxdddddxxxkxxxxkkkkkkxxxxkxkxxkkkxxxxxxxxxxxxxxxdoodddx
oooooollllloxdoooooddoooooooolccc:::c::::,..''''',:lxkkdc;,'''''''',;lxkO0OOOkxkOOOO00Oxxxl,'.....''................'......',;;,''',;;;;;,,,,,,;;;,,;;;;,,;:::::cc:::::;;;:::::::clc:::::;;:;;::;;:;;;,;;cllccclllloooooooolcc:cccccclclllcccccllcloddxxkxxkkkkkkkkkkkkkkkkkkkkxxxxkkkkkkkkxxxxxkxxxxdookOOO
oooooolllllloxdoooooooooooooollcc:;;,''''........',;:cc:;,,'''...'',,,,:dkkdc,,;;cddoooooddlc;'.............................'''''',,;;:::;;,,,;:::;;,,,,,,,;:;;;::::::::::::cccclllllcccccccc::::c:clc;;:llllcllllloooc::loc::::::::ccccclloddolcldolldkOkkxxxxxxkkOOkxxxOOkkkkkkkO00OKKOkkkxkkxkkkkxdodOOO0
ooooooollllooooooooooooooooooooolc:;,''',cc'..'''',,,,,'''''.....'''',,',ld:.',cl::olccllollll:,'............................'''''',,,;:::;,,,,;:clc;,,,,,,;;;,,;;;;::cclllllccccloollllccclc::cccccl:,;cllllllcllolc::::loc::::::::::ccccllox00xollldkOOkxdoodxkkOOkdoodkOOOkkkO00OkOOOOOkxdxxxxxdxxddkkkkO
ooooooollooodxdoodoloolooooooooooolcccccd0k;....''''''''.........''''',''':,...',,:lc:cccc::clc:::,.....................''''.....'''',,;;;;,,,,;;:c:;,,,,,,;;;;,,,;;;:ccccccc:::::cc::;;;;:::cccccccc;,;coolc:;;;cc:;;:::::::::::cccccllllllod0NN0OkkxkOOOOOkkxkkxddooddxkOOOkxxxkkkO0OOOOkxxxxkkxxxkOkxkOkx
kdddooolldxodxololclodoloooddooodollllllodo:'...................;:'''''''.;:,...';:cccccc:::cclc:c:;,''..............................'',,,,'',,,,;;,,,,,,,;;;;;;;;;;::cc::::::;;;:::::;:::::ccccccclc:::::;;;::::codl;;;:c::clllcclllooddddddxk000kkkkkOOOOkOOO0OkxxddxxkkkkkxxxxxxxkkOkxkkkxxxxkkkk0O0OO0OO
Okkxoooooddlooollc::coooolddllllcccccccc:::lc'................':cc:,'''''.',,''',cc::c:::;;::cc:;:c:::;;'..............................'''...''',''''''''',,,,,,,;:c:;;;:::ccc:::::::::::::cccccclllc::;,,;;cc:;clodol:;:lool:cccccolcdOOxdddddxxl:cdOOOKKOkkxkOOO00Okkkkkkkkkxxxxxkxxxxdx0KkxOkxkkxkOOOOkOK
ddkkdoodooolcooolllodlodlcolcllcc:cccodc,,coc:,.............';lcclc:;,'''.';;;;,,;:;;;;::::::::;;;;;;:::::;;'...................................'''''''''''''',,,,;;;,,,;;;:::::::::::::::::cccccll::cc:codool:,,,;loc;;;:lc,,,;ll:locclxxoloddkklccoO00XXKOxxxkkO0K00K0kkkkkkxkkkxxxxkOOkkOkO0Oxdddx0K0kkO0
odxddooxxxkdlllllodxdc:lcccccc:::;:clll;'';c:;,'..      ...,:::;::::;:;;'',:c::;;::;;;;;;;:::,;;,;;,,;;;,,,,,.................................................''''''''''',,,,;;;;,,,,,,,,,,,,,;;;c:;:ol:cll;,,;,,;;::,,,,,;;;;clcclccodkkxdk0KXXOlcoxO0XWWNKOxdxkOOOO0XXOkkkkkxxxkkkkO0KKkdkOOOOdoxOkO00O0Ok
llollllodxdolllcccccc;;::;::::;;;;::cc:,''',;:;,'...........,,,,:::cc:;,.';d0x:;::::;;::::;;;;;,,,,''''','...........  ..  ...........................................',;:clool;............';cc;,,,;:ll;:cc:,,,;;;,,,;clclllooooodxxxOKK0KXNNKkdodk0KXWWXK0kxdkkkOO00KNXOkkkxxxxk0OkO0K0OxdxkO0kdxOOO0KK0kk
dooolllllllllclcccllcc::;:cc:::::::::::;,.','',;;;,'''.....';,'',,,ldl:,.':llc,,::;;:::;::,;;;;,,,'''.'''........'cc'...   ..               ..........................,;::cdOKX0l'......',;;cdxc,;::;:c:,;;;;,,:oo:;,,,cllooccoxkOKXNK0XNNXKOOxdxO0KNWWNXK0OOxxOOOOO0KNNN0OkkkxxkkkxkO0K0Okkkxdxxdxxkxkkkddx
ollllllccllllcclllcccc::::::::::::::::::;,',,'.,:::;;::;;,,',,',,,;:ddl:,....,;;;::::::::;;;;:;''cdc'..'....';::ok00o'..........   ....     .        ....';c:........,;:::cxKNWNXkc;;:c::ccloddo;:ldxc:;,,,,;;,;cccc:;,;cooclcloodOKK00KOkxdxk0XXNNWNXKXK000OkkOO000KNWNXK0kkxxxxxxxxkkkkkxxxddddddxddxkxddd
loxoclc::ccllcc::cccccccc:;;;;:ccc::::::::;,,'......,;;:c;;;:;;:;;;;clc;;,,,;::cccc::::::;;;,;,;;:l;''''..'',;::d0XKkl:;'.';;..,'...''..'.............'',,o00l,,'',,,,;:c::ldO00OOxdoool:cllooooc::cxxol:,,;:;,;:c:::cclxkllolooxO000kkkkO0KXNWWNK000KXXXK000OOO0KXNWNXKK0Okkxxxxxxxxxxddxxxxkkkkkkxxdxxxddd
lloollcccccccccccccccccccc:;'',;:ccccc:::::::;,'......',;',:odlcc:::::c::;;::c:loxdlcccc:::;:;,,,''',::,,,,;;,;cok0kxkkxl:d0Ol,;;',,,,,;::,;:;,;;:cc::;;;ccooc:cc:c:;,,;;;;;:lloxkdooooooolllc:ccccox0koc:::::cldxollldO0OddO0OOO00000KNNNNXK00OOO0KNNKKK000KKKXNWWNX00KKOkkkxxxxxxxxxxddddkkxxxkOkxdddooodd
llllllcllcllllccccllc:ccccc:,'.',,:llloolcc::c::;,,,:c;...';xKd:lc;;;:::cc:ccclxKNKdllllccc::c::;;,,:lc;;:ol;;:lxKXOxdokxcldoc;:cc::::lddl:ccloollolll:;,:;,:clooddl;',,,;;;coddxxoodddxklccc::loodxxdoloolodoododOOOOOkkOO0NNKKXNXXNXXK0OOOkOKXXXXXKKKKKKKXXNWWNXKOOKXXOkxxkkxxxxxxxk0OxdxkOkOOkkkxoooododd
llllllcllllloollcllooc::ccccc:,'..',:::lolcccccc:::::::;;,,,;;;''....''',;;;;:cdO0klccclccllllodxdoollc:;;coooc:cdOkoooddlloollodlcoxlloolcclolxOocc::;cdko:clloolllc,'',,:clddddddkkodxxddkxddoloooooddx0K0OkO0OOKNNXXXKXNNNXXKK0kOKK000KKXXXXKKKKKKXXNNWWNNXK00OOKNNXOkxxdddxkxxxddxOOkxxddxkxxxddoddxOOdo
lllllllllcccoxxoloddoc:clolcc:;::,'.''''',;:::cllllcccccc:ccccc:;'''..'......'',;;;,,,;;:::::::cccclc:cc:::::clccxOkddxxk0Kkdookkdx0Ooclooxxdxk00xolccldOKdc::::;;;;;,,'.',;:ldxxdxxxx0XXK0OO0KOkkOOO0KKKXNNNXNNNXXK000OkxkkxxxxO00XXXXKKKKKXKKXNXNWNNNNXK0OOkk0XNNXKOkxxxxxddxxdxdddxxkkxxxdddx00dodxxdxkdo
lllllllllcclodOKkxdolllldxocccccc::;;,,,.....',;;::lolooooooodxdollc:::;,,,,,''''......''',;:;:c;,:lc::;::::clolodxddooodO0kdoloodxdooodddoolxKWWXOddxxdxOkdooollodlldoooodxx0XKOkKK0KXXXXXXKKKKX000OOOOOOOOkxxxxxxddxxxxkO0KXXXXXXXKKKXXXXNWWWNNXXK0OkxxxkO0KXNXXKOxxxkOkxxxxxxxxxxxkOkxxxxxxddxxdoodoooooo
olllllllllllloxOkdollllloooolcccc::clllc,,,','....',,,;;::clllloodxodddolllllccc:::;;;,,'',:ldkOl',:;,',;:::;;:;::c:clc:clloxoccloollododkdoloOXNNX0OkxkO0KXK0kxOK0xO00OOOOOO0K0kk00xk0xxxxkxdoddlccllllllodddk000KXK0KXNNXXXXNNNNNWNNNNXNXXK00kxddxkkk0KXNWWWNXOO00kkO00K0OOO0kxk0OOOOkkxdk0Okxdooddooloool
odddlloko:cdxxollllddllolclllcccccccokollloccc;,',,'''......'',;:;ccccloooooooddxOdlodoccccclokkoc:;;,,,,:ol,','.';,''''',,;;,,,;;,'',;;cooolloxkOOxc:::cokOkoc:col:lxxllollldkdlclllxdlldkkxdxO0OkkO0KK0XXXXXXNNXNNNXNNNNWWWNNNNXKO00kddddoodxxkO0XNNNNNXKKXK0Ok0XK000xx0000KNXOxkO0KOxdxddxxxdoookkdlollll
xOOO0kodocclollllllllcllllcclcclollllolllcccccccccc;:l:;:;''''..'...''',,,:c:;:cclllloolooooodxxxOkdodolodddoodollolcoolcooll::coc:::;::codxdxddkxxxdddolloddoloddooxO0OO0OkO000OkO00000OOKKKXKOKXXXXXXNXNNNNNNNNXXXKXX0OOkxxdddxkdodxxxk000KXNNNWWNK0OO0kddddO0OkxkOXKOkkkkOKK0OxxxO0kxddoooooooooooollllll
lod0N0ddxolodxollodolllllllllldddolllloollclllolllcccccclcc::::::;,,',;,''''',,'..''''',;:;,;::::cclcllodolloookkodkdkOxkkddkkxkxdxddollddxk0K0OO00kkOOOOOk00OOO0OO0000KXK00KK0KK0KXKKXK0KK00K0O0KOkkOOkxkkxddoodddooddoodddxxkO0XKKXNNNNNXXXXNWWWNXkdddxxxxxxkOOxdddxOOO00Oxxxxxxxk0Oxxxdoooooooollolllllll
ccoO0kdkxooloxddxkKOodOOOkdllloodxdllloolclccllldolclolcclccldocc:loc::c::c::lllc;,;,,,;oo;';;''..'''''''',,,,,;;;:::clldxxolodollxxllcclooddx0XKOkxxkkxxkOOkddkkdxOOkkxkxdxxkkxdoddoddllolccc:clcc::cc::clccllodkOO0KKXXNNNNXNNNXNNKKKKOkkkOKNWWWNKxdddxkkxddxxkxxxkkOOO00kdddddddddddxxddooooooolollllllll
ooxOkxxdxxxddkkOOOKKO0XKOkxkxllodOkddooolllloddollllxkdlllollolcccllc;;::::::clollllccllodlcclol::cc::c:ldxo:;,;::;;;;:lO0dc;,:ll::;,;;;;;::cloxkOkollccclooc:lol:ldolccllcccolclollclooooddxxxkOOkxk000O0XK00KXXKKXNNXKXXXK000000K0xxxdoooxOXWWWNKkddddxxdddxxkkkkOkkxxdddddddddddddddddddooooooooxdlllllll
loxO0K0xxO0Ok0KKO0KXXXXKkkkkxoodooxkxoloxkkOKK0kkxoodooxxoodlclcccclc::::;;::coxxdolcc::cc:::cccccclcllllodolllodddlloddxkdddooxdodolddddoooodx0XNKkxxddkOOkkdxOOkOOOOOO0KOkkkOOOO0K00K0OOO0000KKK00KKKXK0KK0OO00Ok00kkkkOOxdxxodxkxdooooodx0XNNK0kddddodddxxxxxxxxxdddddddddddddddddx0XXXOdoooollooolllllll
oxkxk0OO0KKKK0Okxk00KKXKkxxxkkxxxxk0Oxxxk000OxOOO0Odooloolllccloxdolccccc:::cd0NKkol:::::::;;;;::;::::::cc:::ccccooloodolllloolcllolldxoodooodONN0xddooodxkkxdxxxxxdxkxxO0kkkkkkxxkkkxxxxddxxxkOOkxxxxxxxxdxxddddddddddodkOdoxxdddddoooooddxO00OOkxdddooooooooooooooddddddddddoddddddONMMWKxooolllllllllllll
dOOdodxKNNXKKKOdx0KKXKKXOxkO0KXKkk0X0kOOxk00xddxkkxoodocccllccldOkdollllcccccokOkoc:::::::;;;;::;;;;;ccclc::::::::::ccc::::::::::::ccccccclllx0KOolllcccoddxxxxolllllooooooddddooddooooodddxxxkkkO0Okxooddxkoollodooooddddxxxddddddoooddddxxxkkxdddddddoooooooooooooooodddddddoooooddx0XXKkdoollllllllllllll
odOkxddxk00O0XOdxOKKKKKKOxkkxOXOdx0KOdddddddddlodollcllcccccccclllllllldolllllllcc:::;::::;;;;::;;;;:cc::::::lxl:cc::::::::c::::c::ccccccccccloollccccccox0XXOxlllllllllllodddoddxxoooodddddxxxk0XNNXOdoodO0xooooooooooddxOOkxddddddooddddodddO0kddddddddoooooooooooooooodddooooooooooddddoooolllllllllllccc
dxOOxdoooddxkkkO000kdxOkdoxkxkkdodxkkoodoooollllllllccccccccccclddollldOxllllllllc:;;:::::;;;;;;;;;;:::::::::lol:::::::::::cc::cccccccccccccccccccccccclokKK0kollllccllloodxkkOO00Okxodddooddxk0NWMMWXOdooddoooooolooooooxO00kxdddddddddooooddxKX0kdddddooooooooooooooooooddoooooooooooooollllllllllllcccccc
oooolodooxxdddkKKkxdodxdoloxOxddolodoloollloxOOkollcccccccccccclddolclllllllllclddc;;:;:::;;;;;;;;;::::::::::::::cllcc::::::::cccllllodollcccccccccccclldkkkxllllcllloooodxxOKNNNNNNX0kxxdodddx0NWWWWXOdoddoolodxdooooooddxkOkxdddddddoooooddddxOXN0xddddooooooooooooooooooddoooooooooooolllllllllllcccccccc
lodooodxddooodxkdoodxxdlcclllllolccllcccccclONWNklcccccccccccccccccccclllllllccloc::::;:::;;;;;;;;;::::::::::::::clccccc:::::cclllllod0klcccccccclllllllxOkxolllllooodddxkOKXNWWWWMWWWN0kxdoddxOKXXKOxdddxxooloOOdooooddddxxxxxxxdddddddddoddddddkK0xddddooooooddoodddoooooodoooooooooooolllllllllcccccccccc
cloxxloxxlllloxOkolllllccclccccc:cccccccc:;;cx0Kklcccccccccccccccccccccllcllcc:::::::::::cc:;;;;;;;;:::::::::::::ccccccc:::::clllloodkKklcccccclllooooooooooooooooddxxOO00KKKKXXNWWWMMWNKkxddoddxxxdooodxdolllooooooodxkOkxxxkkkkddddddddddoddddddddddddddoooooodooooooooooodoooollllloxdllllllllccccccccccc
cccodolcc::cdOXWNOlccclcccccc:;;;;;::cccc:;;;;;ccccccccccccccccccccccccllllccc::::::::::::::;;;;;;;;;:::::::::::::::ccc::::::clllloook0xcccccclloooodxxxddoodoooddxxk0XOdddddkO0KNWWWMMMWX0kxdooooooooooolllllloooooodOKKOkkxkkkkxdddddddddddxxxxddddddddddoooooooooooooooooooooolllllloolllllcccccccccccccc
cccldolc:::clx0KOdllccccccc:;;;;;;;;;;:cllc::::cc:ccclllcccccccccccccccccllc:::::::;;::::;;;;;;;;;:;:::::::::::::::::::::::::clllloook0occccclloooddk00xllllllloodxxOK0dlooddddxk0KNNWWWWWNOxdooooolooollllllllooooodxkOkkkOkkOOOkxddddddddddk0KOxddddddddoooooooooooooooooooooollllllllllllllcccccccccccccc
cccccccc:,,,;:cllclccccccc:;;;;;;;;;;;;:cc::::cooccccoxocccccccccccccccclol::clc:::::::::;;;;;;;;;:::::::::::::::::::c:::::::clllooodkklcccccllooddx0Oxocccccccloodxk0kllldxOK0xdxOKXNWWWWWXkdooooooollllllllllooodddxddxOkxkkOOOkxddddddddddxkOkxdddddddoooooooooooooooooooooooolllllllllllllcccccccccccccc
ccccccccc:;;;;:ccccccccccc:,,,,,,,,,,;;;;;:::coOxlloddlcccccccllccccccccllcolclccc:::::::;;;;;;;;;;:::::::::::::ccccllccc::::clllooodOxccccclloooddx0kolccccccclooddkOxlllodkO0kdodk0KNNNWWN0xdooooollllllllllooloooddddxkxxkOO00Oxddddddddddxxxxxddddddooooooooooooooooooooooolllllllllllllllcccccccccccccc
ccccccccc:;;::::clcccccccc:,,,,,,,,;;;;;;;;:::ccloxkxocccccccoxolccccccloclkxcccc::::::::;;;;;;;;;;::::::::::::ccllllllllllccllllooodOxccccclooooodxxollllcccccloodxkOxllllooodoooodk0KXXNWWXkdoooolllllllllllllloooodddxxxxO0000OxddddddddxkKXKOkxxxdddoooooooooooolllooooolllllllllllllllllcccccccccc:cc::
cccccccc:;;;::ldollc::::cc:;,,,;;;;;;;;;;;;;:cccdkkolcccccccclllcccccccooc:ccccc:::c::::::;;;;::::::::::::::::clllllllllloollllloooodkdc:ccclooooodddoooollllllooddxxkxoooooooddxdodxk0KXNWWN0doooollllodolllllloooddodxxxkkO0000Okddddddddx0NWNXKOkxdddoooooooooollllllllllllllllllllllllllcccccccccc::::::
cccccccc::;:::oxdc:;;;;;;;;,,;;;;;;;;;;;;::::cclddlccccccccccccccccccclolccccc:::::::::::::;;::::::::::::cc::clloolllllllooolllloooodddolcccoooodddxkxoddooooooodddxxkkkkkkOOOkkkddxk0KXWWWWWKxooooolllooolllllllodxdddxkO0K00000OkdddddddxxOXNWWNKOxxdooooooooollllllllllllllllllllccccccccccccccc:::::::::
cccccccccc:::::cc:;;;;;;;,,,,,,;;,;;;;;;;;;;;::ccccccccccccccccccccccccllcclcc::::::::::::::;::::::::ccccllc:clloooloolloooooloooooooodxdlccoooddddxOxoolooooooddddxxk00kxxxxxxxxxkO0KXNWWWWN0xdooollooollooolloooodddxk0XWWXK00OOkdddxxxxxk0NWMMWKOkxdooooddooooodddollllllllllcccccccccccccccccc::::::::::
ccccccccccccccccc::;;;;;;;,,,,,,,,,,;;;;;;;;;;;:::ccccccccolccccccccccclcclol:::::::::::::::::::::ccloollllc::clllllooooooooooooooooooodxdccloooddddxkkdllllllooddxxk0XOoooodxkkkO0KXNNWWWWN0xdoooolloooloddoloooooddxxOKWWWNX0OOOkxdxxxxxxk0WMMMWKOkxoooodkkdooodk0Oxollllllllcccccccccccccccccc:::::::::::
        """
        print(portrait + "\n" + assistant_reply)
        
        # 【步骤7：检查AI回复是否表示结束】
        reply_cleaned = assistant_reply.strip().replace(" ", "").replace("！", "").replace("!", "").replace("，", "").replace(",", "")
        if reply_cleaned == "再见" or (len(reply_cleaned) <= 5 and "再见" in reply_cleaned):
            print("\n对话结束")
            break

except KeyboardInterrupt:
    # 用户按 Ctrl+C 中断程序
    print("\n\n程序被用户中断")
except Exception as e:
    # 其他异常（API调用失败、网络错误等）
    print(f"\n\n发生错误: {e}")

