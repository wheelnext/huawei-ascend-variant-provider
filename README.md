# Huawei-ascend-variant-provider
A variant provider plugin for the Wheel Variant upcoming proposed standard that enables automatic detection and selection of Ascend NPU-optimized Python packages.


# How it works
## Variant Property Format
Variant Properties emitted follow a three-tuple structure
```
namespace :: feature :: value
```
Examples:
- `ascend :: npu_type :: 910b` - Means: This wheel can be only used on Ascend A2 series.

## Detection Process
1. **Initialization**: The plugin uses Ascend npu-smi tool to query hardware information
2. **Hardware Detection**: Identifies all Ascend NPUs and their types.
3. **Property Generation**: Creates variant properties in the format `ascend :: feature :: value`

# Usage
## Test on Local
### 1. Prepare Your Project

Here we use `python-helloworld` to do the fast test, clone the source code
```
mkdir -p /workspace
cd /workspace
git clone https://github.com/dbarnett/python-helloworld.git

cd python-helloworld
```
Add variant configuration to your `pyproject.toml`:
```
# add below lines to the end of pyproject.toml

[variant.default-priorities]
namespace = ["ascend"]

[variant.providers.ascend]
requires = ["huawei-ascend-variant-provider>=0.0.1,<1.0.0"]
enable-if = "platform_system == 'Linux'"
plugin-api = "huawei_ascend_variant_provider.plugin:AscendVariantPlugin"
```

Build the wheel for `python-helloworld`
```
python -m build --wheel
```

### 2. Inject Property into Wheels

We use [`variantlib`](https://github.com/wheelnext/variantlib) to add the property of Ascend NPU type into wheels.

Install variantlib from source
```
# we have to install from source at this time, because the version of `variantlib` on pypi is incompatible with `uv-wheelnext`

cd /workspace
git clone https://github.com/wheelnext/variantlib.git

cd variantlib
uv pip install --system .

variantlib --version
# variantlib version: 0.0.2
```

Install `uv-wheelnext`
```
# Linux

cd /workspace
curl -LSf https://astral.sh/uv/install.sh | INSTALLER_DOWNLOAD_URL=https://wheelnext.astral.sh sh
```

Now we can use `variantlib` to inject hardware information into the built wheel
```
mkdir -p /workspace/wheels
cd /workspace/wheels

variantlib make-variant \
    -f "/workspace/python-helloworld/dist/helloworld-0.1-py3-none-any.whl" \
    -o "./" \
    --pyproject-toml "/workspace/python-helloworld/pyproject.toml" \
    --property "ascend :: npu_type :: 910b" \
    --skip-plugin-validation
```
In the same way, we can inject `310p` property into wheels
```
variantlib make-variant \
    -f "/workspace/python-helloworld/dist/helloworld-0.1-py3-none-any.whl" \
    -o "./" \
    --pyproject-toml "/workspace/python-helloworld/pyproject.toml" \
    --property "ascend :: npu_type :: 310p" \
    --skip-plugin-validation
```

### 3. Installation Test
Copy [huawei_ascend_variant_provider-0.0.2-py3-none-any.whl](./docs/huawei-ascend-variant-provider/huawei_ascend_variant_provider-0.0.2-py3-none-any.whl) into `/workspace/wheels/`

Use the following command to test installation
```
uv pip install --no-index --find-links ./ helloworld --system -vv
```
If you are running this command on Ascend A2 platform, you will see the key log like the following
```
TRACE Found namespace ascend with configs VariantProviderOutput { namespace: VariantNamespace("ascend"), features: {VariantFeature("npu_type"): [VariantValue("910b")]} }
TRACE Received variant metadata for: helloworld-0.1 @ file:///workspace/wheels
DEBUG Using variant wheel helloworld-0.1-py3-none-any-38edb458.whl
DEBUG Selecting: helloworld==0.1 [compatible] (helloworld-0.1-py3-none-any-38edb458.whl)
```
where `helloworld-0.1-py3-none-any-38edb458.whl` is injected `910b` property
```
$ variantlib analyze-wheel -i  helloworld-0.1-py3-none-any-38edb458.whl

variantlib.commands.analyze_wheel - INFO - Filepath: `helloworld-0.1-py3-none-any-38edb458.whl` ... is a Wheel Variant - Label: `38edb458`
############################## Variant: `38edb458` #############################
ascend :: npu_type :: 910b
################################################################################
```

You can use `ASCEND_VARIANT_PROVIDER_FORCE_NPU_TYPE` to overwrite detection for functional test
```
export ASCEND_VARIANT_PROVIDER_FORCE_NPU_TYPE=310p
```

In this way, you can install the wheel with property of `310p`
```
uv pip uninstall --system helloworld

uv pip install --no-index --find-links ./ helloworld --system -vv
```
Then, you will see `310p` wheel is installed
```
TRACE Found namespace ascend with configs VariantProviderOutput { namespace: VariantNamespace("ascend"), features: {VariantFeature("npu_type"): [VariantValue("310p")]} }
TRACE Received variant metadata for: helloworld-0.1 @ file:///workspace/wheels
DEBUG Using variant wheel helloworld-0.1-py3-none-any-aabc2c9e.whl
DEBUG Selecting: helloworld==0.1 [compatible] (helloworld-0.1-py3-none-any-aabc2c9e.whl)
```
where `helloworld-0.1-py3-none-any-aabc2c9e.whl`
```
$ variantlib analyze-wheel -i  helloworld-0.1-py3-none-any-aabc2c9e.whl

variantlib.commands.analyze_wheel - INFO - Filepath: `helloworld-0.1-py3-none-any-aabc2c9e.whl` ... is a Wheel Variant - Label: `aabc2c9e`
############################## Variant: `aabc2c9e` #############################
ascend :: npu_type :: 310p
################################################################################
```