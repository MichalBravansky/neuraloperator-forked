"""
Callbacks store all non-essential logic
required to run specific training scripts. 

The callbacks in this module follow the form and 
logic of callbacks in Pytorch-Lightning (https://lightning.ai/docs/pytorch/stable)
"""

import sys

from neuralop.training.patching import MultigridPatching2D

class Callback(object):
    """
    Base callback class. Each abstract method is called in the trainer's
    training loop at the appropriate time. 
    """
    def __init__(self):
        self.state_dict = {}
    
    def _update_state_dict(self, **kwargs):
        self.state_dict.update(kwargs)

    def on_init_start(self, **kwargs):
        self._update_state_dict(**kwargs)
        pass

    def on_init_end(self, *args, **kwargs):
        pass

    def on_before_train(self, *args, **kwargs):
        pass

    def on_train_start(self, *args, **kwargs):
        pass

    def on_epoch_start(self, *args, **kwargs):
        pass
    
    def on_batch_start(self, *args, **kwargs):
        pass

    def on_load_to_device(self, *args, **kwargs):
        pass
    
    def on_before_forward(self, *args, **kwargs):
        pass

    def on_before_loss(self, *args, **kwargs):
        pass
    
    def on_batch_end(self, *args, **kwargs):
        pass
    
    def on_epoch_end(self, *args, **kwargs):
        pass

    def on_train_start(self, *args, **kwargs):
        pass

    def on_before_val(self, *args, **kwargs):
        pass
    
    def on_val_batch_start(self, *args, **kwargs):
        pass

class SimpleLoggerCallback(Callback):
    """
    Callback that implements simple logging functionality 
    expected when passing verbose to a Trainer
    """

    def __init__(self):
        super().__init__()
    
    def on_train_start(self, **kwargs):
        self._update_state_dict(**kwargs)

        train_loader = self.state_dict['train_loader']
        test_loaders = self.state_dict['test_loaders']
        verbose = self.state_dict['verbose']

        n_train = len(train_loader.dataset)

        if not isinstance(test_loaders, dict):
            test_loaders = dict(test=test_loaders)

        if verbose:
            print(f'Training on {n_train} samples')
            print(f'Testing on {[len(loader.dataset) for loader in test_loaders.values()]} samples'
                  f'         on resolutions {[name for name in test_loaders]}.')
            sys.stdout.flush()
        
    def on_epoch_start(self, epoch):
        self._update_state_dict(epoch=epoch)
    
    def on_batch_start(self, idx, **kwargs):
        self.state_dict.update(idx=idx)

    def on_before_loss(self, out):
        if self.state_dict['epoch'] == 0 and self.state_dict['idx'] == 0 \
            and self.state_dict['verbose']:
            print(f'Raw outputs of size {out.shape=}')

class MGPatchingCallback(Callback):
    def __init__(self, levels, padding_fraction,stitching):
        super().__init__()
        self.levels = levels
        self.padding_fraction = padding_fraction
        self.stitching = stitching
        
    def on_init_end(self, model, **kwargs):
        self.patcher = MultigridPatching2D(model=model, levels=self.levels, 
                                      padding_fraction=self.padding_fraction,
                                      stitching=self.stitching)
    
    def on_batch_start(self, **kwargs):
        self._update_state_dict(**kwargs)
        x,y = self.patcher.patch(self.state_dict['sample']['x'],
                                 self.state_dict['sample']['y'])

        self.state_dict['sample']['x'] = x
        self.state_dict['sample']['y'] = y
    
    def on_before_loss(self, out):
        self._update_state_dict(out=out)
        self.state_dict['out'], self.state_dict['sample']['y'] = \
            self.patcher.unpatch(self.state_dict['out'],
                                 self.state_dict['sample']['y'])
    

        




