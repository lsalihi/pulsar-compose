class Pulsar < Formula
  desc "AI workflow orchestration engine"
  homepage "https://github.com/lsalihi/pulsar-compose"
  url "https://github.com/lsalihi/pulsar-compose/archive/refs/tags/v0.1.1.tar.gz"
  sha256 "5d59deeefb854b2c9c60dcbb0a66300bb6e0cc981edcd37c7fd8790154db082d"
  license "MIT"

  depends_on "python@3.11"

  def install
    # Install via pip
    system "pip3", "install", "--prefix=#{prefix}", "."
  end

  test do
    system "#{bin}/pulsar", "--version"
    system "#{bin}/pulsar", "--help"
  end
end