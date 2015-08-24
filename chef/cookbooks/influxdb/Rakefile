require 'rake'
require 'rake/testtask'
require 'rubocop/rake_task'
require 'foodcritic'

task default: 'test:quick'

namespace :test do

  RuboCop::RakeTask.new

  Rake::TestTask.new do |t|
    t.name = :minitest
    t.test_files = Dir.glob('test/spec/**/*_spec.rb')
  end

  FoodCritic::Rake::LintTask.new do |t|
    t.name = :foodcritic
    t.options = {
      fail_tags: ['any'],
      tags: ['~FC001', '~FC007', '~FC017']
    }
  end

  begin
    require 'kitchen'
    namespace :integration do
      desc 'Run Test Kitchen with Vagrant'
      task :vagrant do
        Kitchen.logger = Kitchen.default_file_logger
        Kitchen::Config.new.instances.each do |instance|
          instance.test(:always)
        end
      end
    end
  rescue LoadError
    puts '>>>>> Kitchen gem not loaded, omitting tasks' unless ENV['CI']
  end

  desc 'Run all of the quick tests.'
  task :quick do
    Rake::Task['test:rubocop'].invoke
    Rake::Task['test:minitest'].invoke
    Rake::Task['test:foodcritic'].invoke
  end

  desc 'Run all tests, including test-kitchen.'
  task :complete do
    Rake::Task['test:rubocop'].invoke
    Rake::Task['test:minitest'].invoke
    Rake::Task['test:foodcritic'].invoke
    Rake::Task['test:integration:vagrant'].invoke
  end
end
