#! /usr/bin/ruby

require 'pi_piper'

$last_pulse = Time.now
$current_digit = 0
$dialed = ""
LIMIT = 0.25 # two digits are separated by at least 0.25 seconds

def check_last_digit
  if Time.now - $last_pulse > LIMIT and $current_digit > 0
    $dialed << ($current_digit % 10).to_s
    $current_digit = 0
  end
end

PiPiper.after :pin => 18, :goes => :high do
  check_last_digit
  $last_pulse = Time.now
  $current_digit += 1
end

Thread.new {
  loop {
    sleep 0.5
    check_last_digit
    if Time.now - $last_pulse > 5 and not $dialed.empty?
      puts "dialed #{$dialed}"
      $dialed = ""
    end
  }
}

PiPiper.wait

