class Pulsar < Formula
  desc "AI workflow orchestration engine"
  homepage "https://github.com/lsalihi/pulsar-compose"
  url "https://github.com/lsalihi/pulsar-compose/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "YOUR_SHA256_HERE"  # Replace with actual SHA256
  license "MIT"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/lsalihi/pulsar-compose/releases/download/v0.1.0/pulsar-compose-macos-arm64.tar.gz"
      sha256 "YOUR_SHA256_HERE"  # Replace with actual SHA256 for ARM64
    else
      url "https://github.com/lsalihi/pulsar-compose/releases/download/v0.1.0/pulsar-compose-macos-x64.tar.gz"
      sha256 "YOUR_SHA256_HERE"  # Replace with actual SHA256 for x64
    end
  end

  on_linux do
    url "https://github.com/lsalihi/pulsar-compose/releases/download/v0.1.0/pulsar-compose-linux-x64.tar.gz"
    sha256 "YOUR_SHA256_HERE"  # Replace with actual SHA256 for Linux
  end

  def install
    # The tarball contains a 'pulsar' directory with the executable
    bin.install "pulsar/pulsar"
  end

  test do
    # Test basic functionality
    system "#{bin}/pulsar", "--version"

    # Test help command
    system "#{bin}/pulsar", "--help"
  end
end