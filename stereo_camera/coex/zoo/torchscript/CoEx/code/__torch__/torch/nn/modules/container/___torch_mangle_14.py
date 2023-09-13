class Sequential(Module):
  __parameters__ = []
  __buffers__ = []
  training : bool
  _is_full_backward_hook : Optional[bool]
  __annotations__["0"] = __torch__.timm.models.efficientnet_blocks.InvertedResidual
  __annotations__["1"] = __torch__.timm.models.efficientnet_blocks.___torch_mangle_13.InvertedResidual
  def forward(self: __torch__.torch.nn.modules.container.___torch_mangle_14.Sequential,
    input: Tensor) -> Tensor:
    _0 = getattr(self, "0")
    _1 = getattr(self, "1")
    input0 = (_0).forward(input, )
    return (_1).forward(input0, )
  def __len__(self: __torch__.torch.nn.modules.container.___torch_mangle_14.Sequential) -> int:
    return 2
