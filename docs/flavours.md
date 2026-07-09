# Flavours

In Arkitekt Next, **Flavours** allow you to provide multiple build configurations for the same application. This is essential for supporting different hardware environments (like CPU vs. GPU) or deployment scenarios without maintaining separate codebases.

## What is a Flavour?

A flavour is essentially a specific recipe for building your app into a Docker container. It consists of:

1.  **A Dockerfile:** Defines the environment (OS, libraries, Python version).
2.  **Configuration (`config.yaml`):** Metadata about the flavour, including its description and **selectors**.

When you publish your app, you publish all its flavours. When a user (or the Arkitekt platform) installs your app, it automatically selects the best flavour based on the available hardware and resources.

## Why use Flavours?

*   **Hardware Acceleration:** You can have a `vanilla` flavour for standard CPU execution and a `cuda` flavour that includes NVIDIA drivers and PyTorch with CUDA support.
*   **Resource Management:** You might have a `light` flavour for low-memory environments and a `heavy` flavour that loads large models into RAM.
*   **Dependency Variations:** Support different backend libraries or system tools in separate containers.

## Creating a Flavour

You can add a new flavour to your project using the CLI:

```bash
arkitekt-next kabinet flavour add --flavour <name>
```

**Example:** Adding a GPU flavour

```bash
arkitekt-next kabinet flavour add --flavour gpu --description "CUDA enabled build"
```

This will create a new directory in `.arkitekt_next/flavours/gpu/` containing a `Dockerfile` and `config.yaml`. You can then customize the Dockerfile to include the necessary GPU drivers and libraries.

## Selectors

Selectors are the mechanism Arkitekt uses to match a flavour to a deployment environment. You define them in the flavour's `config.yaml`.

Common selectors include:

*   **`cuda`**: Requires a CUDA-enabled GPU to be present.
*   **`cpu`**: Matches based on CPU architecture (e.g., `arm64` vs `amd64`).
*   **`ram`**: Specifies minimum memory requirements.



### Example `config.yaml`

```yaml
description: "A high-performance GPU build"
selectors:
  - type: gpu
    required: true
  - type: ram
    min: "8GB"
dockerfile: Dockerfile
```

## Building Flavours

When you run `arkitekt-next build`, the CLI will build the default flavour (usually `vanilla`). To build a specific flavour, use the `--flavour` flag:

```bash
arkitekt-next build --flavour gpu
```

## Publishing

When you run `arkitekt-next publish`, you can publish specific builds associated with their flavours. The platform will register these flavours under the same app version, allowing for seamless deployment across diverse infrastructure.
