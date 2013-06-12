#! /usr/bin/ruby

require 'pi_piper'

$end = false

class Dial
  LIMIT = 0.25 # two digits are separated by at least 0.25 seconds

  def initialize
    @last_pulse = Time.now
    @current_digit = 0
    @dialed = ""

    # need lambda bound to local variable for correct scope
    getpulse = lambda {
      check_last_digit
      @last_pulse = Time.now
      @current_digit += 1
    }

    PiPiper.after :pin => 18, :goes => :high do getpulse.call end

    Thread.new {
      loop {
        sleep 0.5
        check_last_digit
        if Time.now - @last_pulse > 5 and not @dialed.empty?
          puts "dialed #{@dialed}"
          $end = true if @dialed == "0000"
          @dialed = ""
        end
      }
    }

  end

private
  def check_last_digit
    if Time.now - @last_pulse > LIMIT and @current_digit > 0
      @dialed << (@current_digit % 10).to_s
      @current_digit = 0
    end
  end
end

Dial.new

while !$end
  sleep 2
end
