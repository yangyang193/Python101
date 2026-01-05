from roles import get_role_prompt, get_break_rules
from logic import should_exit_by_user, should_exit_by_ai
from chat import chat_once

def get_portrait():
    """
    获取ASCII头像
    
    返回：
        ASCII头像字符串
    """
    return """
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
,,,;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;:coxxdc;'....'cdo::odccoddkOkoloxO00kookKXKxc:::::::::::::::::::coxk0XXXXK0OxolclllkNWWNXK0000kkxxxxddodddddOXOlcccccccccccccccccccccccldkKXNXKOkolclllc::::::::::::::::::::ccox0KNNNXKOkoc:::::ccc:::coddc:::::::::::::::::::::::::::::::::::ldO00xlccllc:;;;;;;;;;;;;
,,;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;:cokOkdc,'.....'::;;clldkkoldkkoc:cllccldOKXkl:::::::::::::::::::cxKKKK0kkkO0XX0kdoldk0XXKOxkKXOxkkxkkddddddxO0OkkdlldoccccccccccoxOKXNNX0kdlc:;:::::::::::::::::::::::::cc:::cok0XNWWN0dc::::::::cok00kl:::::::::::::::::::::::::::::::::::cdO00Oxxkkxo:;;;;;;;;;;;
;;;;;;;;;;;;:::::;;;;;;;;;;;;;;;;;;;;;;:coxkkdl;,'......',,,,;cdxdooddoc:coolccloxOOdc::::::::::ccccccllolokXNNXKOkk0XWWWNKOl;lkxoc,cOkccdl:odxxxkOOkxdddxxooOxccccccclok0XNNX0kdoccc::::::::cc:::::::::::::::::::::c::;:cldkOOxolclollc::cokKNXxc:::::::::::::::::::::::::::::::::::cdO0K0Okxdo:;;;;;;;;;;;
;;;;;;;;,,;:coxOOdc;;;;;;;;;;;;;;;;;,,;;:lodl:;,'''''''',,,',;;ccc:codolldkOkxoodkOko:::::::::::cccldOK0kdodxOKNWNKOOKNN0xdxd:ldolc;,:;,,:oo:;lOO00OxdoolllokOocccclok0XNNXKOxolccccccccccccccccc:::::::::::::::::::::::::;;::::::cloxxxdlclox00dc:cc::::::::::::::::::::::::::::::::::lxOOxdol::;;;;;;;;;;;
;;;;;;;,,,,;cd0NWNOc;;;;;;;;;;;;;;;;,,,;;:::;;;;;;;;;;;;,;:c:;,,,;coxkkxxxkO0Oxdxkxoc::::::::::c::cd0NN0xoooxxx0WWNX0000o,,;:::;;cool:::,,coc,;:cd0kdollodkO0xllldk0XNNNX0kolccccccccccccccccccccccccccccccccccccccccccccccc:::;;;;;;:cclodxOOxollllc::c::::::::::::::::::::::::::::::::::::cloooddoc:;;;;;;;;;;
;;;;;;;,'',,;cx0XXOl:;;;col:;;;;;;;;;;;;;;:::::::::::::;;:dxl:;,;:oOKKK0OOkOOkdollc::::::::::cccc::lOXXOxdooxO00XWWNX0xlc;,,:c:,,;:l::do;'';c:',,ckkooodkOkkdoox0XNNNXKOxolcccccccccccccccccccccccccccccccccccccccccccccccccc::::;;,,,;;:clloxxoccccc:ccccc:::::::::::::::::::::::::::::::::::::clodl:;;;;;;;;;;
;;;;;;;,'''',,:ldxoc;:::lxl:;;;;:;;:::::;;;:::::::::::::;;:::;;;;:cdk00KKXXXKOdc::::::::::::ccccccccokKXK0kxxOKXXKXNXOc,::'';c;',c:,;c:;;c:';clc;;:coxxxxxkkk0XNWNXKOOOdlccccccccccccccccccccccccccccccccccccccccccccccccccccccc:::::;;;;:ccccccccccc:::clc::::::::::::::::::::::::::::::::::::::::c::;;;;;;;;;;
;;;;;;;;,,,,,,;:cc:;;::;::;;;;;;;:::::::::::::::::::::::::::ccccc:ccoxkOKXNNNKklc::::::::::ccccccccccclxO0K00OOKXK0K0d;,,;;;,,:;',,''',',c:',lxd:;clodxxxx0XXNNXKOdlcdK0occccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc:::::::c::::::::::::::::::::::::::::::::::::::::::;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;:;;;;;;:::::::::::::::::::::::::cccllllccccok0K00KXNWNOocc:::::::::cccccccccccccclodxxxxO0xdkxo;;;,,,',,,'',;,''',;clcl:;;ccloodk0XXX0kxdlc:;:lxdlcccccccccccccccccccccccccccccccccccllcccccccccccccccccccccccccccccccccccccccc::c:::::::::::::::::::::::::::::::::::::::::::::::;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;:;;;;:::::::::::::::::::::::::::::cccccccccxKNNNK0KXNXOoccccc:ccccccccccccccccccclccccccclccclddolc:,''',,;:coolcokO0KOc;::cldkOKXK0kdlccccccc:cclodoccccccccccllccccccccccccccccllcccccccccccccccccccccccccccccccccccccccccccccccc::::::::::::::::::::::::::::::::::::::::::::::::;;;;;
"""

def main():
    """
    主程序入口
    负责初始化对话历史，运行主循环
    """
    print("=" * 60)
    print("克隆人对话系统 - 带记忆功能")
    print("=" * 60)
    print("\n说明：")
    print("- 对话记录不会保存到文件")
    print("- AI的记忆基于初始记忆文件")
    print("- 输入'再见'可以退出\n")
    
    # 初始化角色设定
    role_prompt = get_role_prompt("姥姥")
    
    # 初始化对话历史
    system_message = role_prompt + "\n\n" + get_break_rules()
    conversation_history = [{"role": "system", "content": system_message}]
    
    print("✓ 已加载初始记忆，开始对话（对话记录不会保存）\n")
    
    # 获取ASCII头像
    portrait = get_portrait()
    
    # 主循环
    while True:
        # 获取用户输入
        user_input = input("请输入你要说的话（输入\"再见\"退出）：")
        
        # 检查用户是否要退出
        if should_exit_by_user(user_input):
            print("对话结束")
            break
        
        # 进行一次对话
        try:
            reply = chat_once(conversation_history, user_input, role_prompt)
            
            # 显示AI回复（带头像）
            print(portrait + "\n" + reply + "\n")
            
            # 检查AI是否表示要结束
            if should_exit_by_ai(reply):
                print("\n对话结束")
                break
                
        except Exception as e:
            print(f"发生错误: {e}")
            import traceback
            traceback.print_exc()
            break

if __name__ == "__main__":
    main()

