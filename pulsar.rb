class Pulsar < Formula
  include Language::Python::Virtualenv

  desc "AI workflow orchestration engine"
  homepage "https://github.com/lsalihi/pulsar-compose"
  url "https://github.com/lsalihi/pulsar-compose/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "YOUR_SHA256_HERE"  # Replace with actual SHA256
  license "MIT"

  depends_on "python@3.11"

  resource "anyio" do
    url "https://files.pythonhosted.org/packages/2d/b8/7333d87d5f03247215d86a86362fd3e324111788c6cdd8d2e6196a6ba833bb7/anyio-4.3.0.tar.gz"
    sha256 "f75253795a87df48568485fd18cdd2a3fa5c4f7c5be8e5e36637733fce06fedb22a"
  end

  resource "click" do
    url "https://files.pythonhosted.org/packages/96/d3/f04c7bfcf5c1862a2a5b845c6b2b360488cf47af55dfa79c98f6a6bf98b5b9c/click-8.1.7.tar.gz"
    sha256 "ca9853ad459e787e2192211578cc907e7594e294c7ccc834310722b41b9ca6de0b23"
  end

  resource "jinja2" do
    url "https://files.pythonhosted.org/packages/7a/ff/75c28576a1d900e87eb6335b063fab47a8ef3c8b4d88524c4bf78f670cce589b/jinja2-3.1.3.tar.gz"
    sha256 "ac8bd6544d4bb2c9792bf3a159e80bba8fda7f0e3ffc030559a35c259bbc82231b"
  end

  resource "pydantic" do
    url "https://files.pythonhosted.org/packages/1f/74/0d009e056c2b6b7a7e6c3d1b7b9b3b8c8c5a6b0b1c6e2b4f0c1b7c5b7c8d9/pydantic-2.6.1.tar.gz"
    sha256 "4fd5c182a2488dc63e6d31c697122c6f80549a8370e8270655f1284b0ea1ba8a0b8"
  end

  resource "pyyaml" do
    url "https://files.pythonhosted.org/packages/cd/e5/af35f7ea75cf72f2cd079c95ee16797de7cd71f29ea7c68ae5ce7be1eda0b83/PyYAML-6.0.1.tar.gz"
    sha256 "bfdf460b1736c775f2ba9f6a92bca30bc2095067b8a9d77876d1fad6cc3b4a43d3"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/a7/ec/4a7d80728bd429f7c0d4d51245287158a1516315cadbb146012439403a9d29b/Rich-13.7.1.tar.gz"
    sha256 "9be308cb1fe2f1f57d67ce99e95af38a1e2bc71ad9813b0e247cf7ffbcc3a4329"
  end

  resource "httpx" do
    url "https://files.pythonhosted.org/packages/78/82/08f8c936781f67d9e6b9eeb8a0c8b4e406136ea4c3d1f89a5db71d42e0e7d/httpx-0.26.0.tar.gz"
    sha256 "451b55c30d5185ea6b23c2c793abf9bb237d2a7dfb901ced6babf33521e260bbbe"
  end

  resource "openai" do
    url "https://files.pythonhosted.org/packages/3d/2e/4f5eaab8e3c61b9c3c8d5e8c5b0a6b4e8c5f5e8c5f5e8c5f5e8c5f5e8c5f/openai-1.12.0.tar.gz"
    sha256 "8c4694e8ba1f4b1b6b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b"
  end

  def install
    virtualenv_install_with_resources

    # Install pulsar
    system "python", "-m", "pip", "install", "-v", "."
  end

  test do
    # Test basic functionality
    system "#{bin}/pulsar", "--version"

    # Test workflow validation
    (testpath/"test_workflow.yml").write <<~EOS
      version: "0.1"
      name: "Test Workflow"
      workflow:
        - type: "agent"
          step: "test"
          agent: "test_agent"
          prompt: "Hello world"
    EOS

    system "#{bin}/pulsar", "validate", "test_workflow.yml"
  end
end