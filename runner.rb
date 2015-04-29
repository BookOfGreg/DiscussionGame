#!/usr/bin/env ruby

#Dir.foreach("./graphs") do |file_name|
[
# "balanced_binary_tree_9999",
# "balanced_20_tree_9999",
# "worst_case_tree_9999",
# "looping_graph_9999",
# "balanced_binary_tree_49999",
# "balanced_20_tree_49999",
# "looping_graph_49999",
# "worst_case_tree_49999",
 "balanced_binary_tree_4999",
 "balanced_20_tree_4999",
 "looping_graph_4999",
 "worst_case_tree_4999"].each do |file_name|
  puts file_name
  next if file_name == '.' or file_name == '..'
  30.times do |num|
    output = `python main.py ./graphs/#{file_name} 1`
    File.open("./results/#{file_name}_result_#{num}", "w+") do |f|
      f.puts output
    end
  end
end
