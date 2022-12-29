from core.grid_search import GridSearch
from core.learner.upgd import UPGDv1LearnerFO, UPGDv1LearnerSO, UPGDv2LearnerFO, UPGDv2LearnerSO
from core.learner.search import SearchLearnerNormalFO, SearchLearnerNormalSO, SearchLearnerAntiCorrFO, SearchLearnerAntiCorrSO
from core.learner.sgd import SGDLearner
from core.learner.anti_pgd import AntiPGDLearner
from core.learner.pgd import PGDLearner
from core.task.label_permuted_mnist import LabelPermutedMNIST
from core.network.fcn_tanh import FullyConnectedTanh
from core.network.fcn_relu import FullyConnectedReLU
from core.network.fcn_leakyrelu import FullyConnectedLeakyReLU
from core.runner import Runner
from core.run import Run
from core.utils import create_script_generator, create_script_runner


task = LabelPermutedMNIST()


gt_grids = GridSearch(
        seed=[i for i in range(0, 30)],
        lr=[2 ** -i for i in range(0, 8)],
        beta_utility=[0.0, 0.5, 0.9, 0.99, 0.999],
        temp=[1.0, 2.0, 0.5],
        sigma=[1.0, 0.5, 2.0],
        network=[FullyConnectedTanh(), FullyConnectedReLU(), FullyConnectedLeakyReLU()],
        n_samples=[50000],
    )

sgd_grids = GridSearch(
               seed=[i for i in range(0, 2)],
               lr=[2 ** -i for i in range(0, 8)],
               network=[FullyConnectedTanh(), FullyConnectedReLU(), FullyConnectedLeakyReLU()],
               n_samples=[50000],
    )

grids = [
    gt_grids,
    gt_grids,
    gt_grids,
    gt_grids,
    gt_grids,
    gt_grids,
    gt_grids,
    gt_grids,
    sgd_grids,
    sgd_grids,
    sgd_grids,
]

learners = [
    UPGDv1LearnerFO(FullyConnectedTanh(), dict()),
    UPGDv1LearnerSO(FullyConnectedTanh(), dict()),
    UPGDv2LearnerFO(FullyConnectedTanh(), dict()),
    UPGDv2LearnerSO(FullyConnectedTanh(), dict()),
    SearchLearnerNormalFO(FullyConnectedTanh(), dict()),
    SearchLearnerNormalSO(FullyConnectedTanh(), dict()),
    SearchLearnerAntiCorrFO(FullyConnectedTanh(), dict()),
    SearchLearnerAntiCorrSO(FullyConnectedTanh(), dict()),
    SGDLearner(FullyConnectedTanh(), dict()),
    AntiPGDLearner(FullyConnectedTanh(), dict()),
    PGDLearner(FullyConnectedTanh(), dict()),
]

for learner, grid in zip(learners, grids):
    runner = Runner(Run, learner, grid, task, learner.name)
    runner.write_cmd("generated_cmds")
    create_script_generator(f"generated_cmds/{task.name}")
    create_script_runner(f"generated_cmds/{task.name}")