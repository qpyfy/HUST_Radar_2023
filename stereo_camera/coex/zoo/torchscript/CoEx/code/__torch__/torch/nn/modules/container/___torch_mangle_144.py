class Sequential(Module):
  __parameters__ = []
  __buffers__ = []
  training : bool
  _is_full_backward_hook : Optional[bool]
  __annotations__["0"] = __torch__.torch.nn.modules.conv.___torch_mangle_143.ConvTranspose2d
  def forward(self: __torch__.torch.nn.modules.container.___torch_mangle_144.Sequential,
    input: Tensor) -> Tensor:
    input0 = (getattr(self, "0")).forward(input, None, )
    return input0
  def __len__(self: __torch__.torch.nn.modules.container.___torch_mangle_144.Sequential) -> int:
    return 1
