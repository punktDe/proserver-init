# ansible-init.rb
class AnsibleInit < Formula
  desc "A Python script that facilitates setting up a Punkt.de Ansible project"
  homepage "https://punkt.de"

  head "git@git.punkt.de:pt/ansible-init.git", :using => :git, :branch => "main"

  url "git@git.punkt.de:pt/ansible-init.git", :using => :git, :tag => "1.0.2"

  depends_on "python@3"

  def install
    bin.install "ansible-init"  # CHANGEME
  end

end
