const { client } = require("../config/twilio");

// SEND OTP VIA SMS
exports.sendOTP = async (req, res) => {
  console.log("📩 /send-otp hit with body:", req.body);
  const { phone } = req.body;

  try {
    const result = await client.verify.v2
      .services(process.env.TWILIO_VERIFY_SERVICE_SID)
      .verifications.create({
        to: phone,        // e.g. "+919136147222"
        channel: "sms",   // SMS
      });

    console.log("✅ Twilio verification created:");
    console.log(result);

    res.status(200).json({
      message: "OTP sent successfully via SMS",
      status: result.status,
    });
  } catch (err) {
    console.log("❌ Twilio error:");
    console.log(err);

    res.status(400).json({
      error: err.message,
      code: err.code,
      moreInfo: err.moreInfo,
    });
  }
};

// VERIFY OTP VIA SMS
exports.verifyOTP = async (req, res) => {
  console.log("📩 /verify-otp hit with body:", req.body);
  const { phone, code } = req.body;

  try {
    const result = await client.verify.v2
      .services(process.env.TWILIO_VERIFY_SERVICE_SID)
      .verificationChecks.create({
        to: phone,
        code,
      });

    console.log("✅ Verification check result:");
    console.log(result);

    if (result.status === "approved") {
      res.status(200).json({ message: "OTP verified successfully" });
    } else {
      res.status(400).json({
        message: "Invalid OTP",
        status: result.status,
      });
    }
  } catch (err) {
    console.log("❌ Twilio verify error:");
    console.log(err);

    res.status(400).json({
      error: err.message,
      code: err.code,
      moreInfo: err.moreInfo,
    });
  }
};
