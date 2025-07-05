from legged_gym import LEGGED_GYM_ROOT_DIR, LEGGED_GYM_ENVS_DIR

from legged_gym.envs.GO2_cannot_deploy.go2_config import GO2Cfg_Yu,GO2CfgPPO_Yu
from legged_gym.envs.GO2_cannot_deploy.dev_config import WEILANCfg_Yu,WEILANPPO_Yu
from legged_gym.envs.GO2_Stand.GO2_Handstand.Go2_handstand_Config import GO2Cfg_Handstand,GO2CfgPPO_Handstand


from .base.legged_robot import LeggedRobot
from .GO2_cannot_deploy.Go2_env import Go2_env
from .GO2_Stand.GO2_Handstand.Go2_handstand import Go2_stand
from legged_gym.utils.task_registry import task_registry
from .lite3_stand.Lite3_handstand_Config import LITECfg_Handstand, LITECfgPPO_Handstand
from .lite3_stand.Lite3_handstand import Lite3_stand
from .lite3_jump.lite3_jump_config import Lite3JUMPCfg, Lite3JUMPPPO
from .lite3_jump.lite3_jump_robot import Lite3Jump
from .m20_stand.m20_handstand_Config import M20HandstandCfg, M20HandstandCfgPPO
from .m20_stand.m20_handstand import M20stand




task_registry.register( "go2", Go2_env, GO2Cfg_Yu(), GO2CfgPPO_Yu())
task_registry.register( "WEILAN", Go2_env, WEILANCfg_Yu(), WEILANPPO_Yu())
task_registry.register( "go2_handstand", Go2_stand, GO2Cfg_Handstand(), GO2CfgPPO_Handstand())
task_registry.register( "lite_hs", Lite3_stand, LITECfg_Handstand(), LITECfgPPO_Handstand())
task_registry.register( "lite_jump", Lite3Jump, Lite3JUMPCfg(), Lite3JUMPPPO())
task_registry.register( "m20_hs", M20stand, M20HandstandCfg(), M20HandstandCfgPPO())

# print("注册的任务:  ",task_registry.task_classes)