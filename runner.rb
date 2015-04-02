#!/usr/bin/env ruby

Dir.foreach("./graphs") do |file_name|
#["balanced_tree_9999",
# "balanced_tree_19999",
# "balanced_tree_29999",
# "balanced_tree_39999",
# "balanced_tree_49999",
# "balanced_tree_59999",
# "balanced_tree_69999",
# "balanced_tree_79999",
# "balanced_tree_89999",
# "balanced_tree_99999"].each do |file_name|
  puts file_name
  next if file_name == '.' or file_name == '..'
  30.times do |num|
    output = `python main.py ./graphs/#{file_name} 0`
    File.open("./results/#{file_name}_result_#{num}", "w+") do |f|
      f.puts output
    end
  end
end
